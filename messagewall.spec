# TODO: separate firestring and firedns packages (with their own -devel and -static)?
Summary:	An SMTP proxy with lots of features
Summary(pl):	Rozbudowany serwer proxy dla SMTP
Name:		messagewall
%define firestring firestring
%define firedns firedns
%define firestring_version 0.1.23
%define firedns_version 0.1.30
Version:	1.0.8
Release:	0.3
License:	GPL
Group:		Networking
Source0:	http://messagewall.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	c8bb5538b4f004b56ba680d50c549b8f
Source1:	http://messagewall.org/download/%{firestring}-%{firestring_version}.tar.gz
# Source1-md5:	f5d1b6fedbbd4137483efb3864d772b6
Source2:	http://messagewall.org/download/%{firedns}-%{firedns_version}.tar.gz
# Source2-md5:	0e18e14615036555183ee01b43fffd3c
Source3:	messagewall.init
Patch0:		messagewall-rfc_violation.patch
URL:		http://meesagewall.org/
BuildRequires:	openssl-devel
PreReq:		rc-scripts
Requires(post,preun):/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MessageWall is a free software SMTP proxy. It sits between the outside
world and your mail server and keeps out viruses, spam and mail
relaying. Unlike many existing ISP-level filtering solutions, it
offers customization of filtering features on a per-address basis.
MessageWall employs a scoring system that allows message rejection
based on multiple rules with different weights, and header tagging
when the message doesn't reach the threshold.

MessageWall also supports strong relay authentication based on source
address or SMTP AUTH PLAIN or LOGIN methods, as well as SSL/TLS
connections from clients and to the backend server.

MessageWall organizes filtering customizations into profiles . The
configuration file defines a default profile, and a seperate file
specifies addresses and domains with profiles other than the default.
Each profile contains a set of rules for how to filter mail.

%description -l pl
MessageWall to serwer proxy dla SMTP opublikowany jako wolne oprogramowanie.
Jego miejsce znajduje siê pomiêdzy twoim serwerem pocztowym a ¶wiatem, a jego
zadanie to utrzymaæ z dala wirusy, spam oraz zarz±dzaæ uprawnieniami
(relaying). Odró¿niaj±cym czynnikiem od wielu innych us³ug tego typu, jest to,
¿e oferuje swobodn± konfiguracjê na poziomie ka¿dego adresu email. MessageWall
stosuje system oceniania pozwalaj±cy na odrzucaniu wiadomo¶ci na podstawie
szeregu regu³ z ró¿nymi wagami i taguj±cy wiadomo¶æ w nag³ówku, je¶li poziom
oceny do odrzucenia nie zostanie osi±gniêty.

MessageWall wspiera tak¿e zaawansowane techniki autentykacji: adres ¼ród³owy,
SMTP AUTH PLAIN lub LOGIN, jak równie¿ sesje SSL/TLS od klientów oraz do
w³a¶ciwego serwera poczty.

MessageWall pobiera regu³y filtrowania z profili. Plik konfiguracyjny
definiuje profil domy¶lny, a dodatkowy plik okre¶la adresy i domeny, do
których nale¿y stosowaæ profil inny ni¿ domy¶lny. Ka¿dy profil zawiera szereg
regu³ dot. filtracji wiadomo¶ci.

%prep
%setup -q -n %{name}
tar zxf %{SOURCE1}
tar zxf %{SOURCE2}

%patch0 -p0

%build
export CC="%{__cc}"
export CFLAGS="%{rpmcflags} -I../firestring" 
# note: configure scripts are not autoconf-generated

cd %{firestring} 
./configure 
%{__make} 

cd ../%{firedns} 
echo "-L../firestring -L../firedns -I../firestring -I../firedns" >firemake.ldflags
./configure 
%{__make} 
cd ..

echo "-L./firestring -L./firedns -I./firestring -I./firedns" >firemake.ldflags
echo "`cat firemake.cflags` -I/usr/include/openssl" >firemake.cflags
export CFLAGS="%{rpmcflags} -Ifirestring -Ifiredns" 
export CONFDIR=%{_sysconfdir}/mwall
./configure

%{__make} \
	PREFIX=%{_prefix} 

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_mandir}/man{1,5},%{_includedir},%{_libdir},%{_bindir}} \
	$RPM_BUILD_ROOT{%{_sysconfdir}/mwall,/etc/rc.d/init.d}

%{__make} install -C firestring \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	INSTALL_USER="`id -u`" \
	INSTALL_GROUP="`id -g`"
	
%{__make} install -C firedns \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	INSTALL_USER="`id -u`" \
	INSTALL_GROUP="`id -g`"
	
%{__make} install \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	CONFDIR=$RPM_BUILD_ROOT%{_sysconfdir}/mwall \
	INSTALL_USER="`id -u`" \
	INSTALL_GROUP="`id -g`"

#install conf/messagewall.conf $RPM_BUILD_ROOT%{_sysconfdir}/mwall
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/messagewall

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add messagewall
if [ -f /var/lock/subsys/messagewall ]; then
        /etc/rc.d/init.d/messagewall restart >&2
else
        echo "Run \"/etc/rc.d/init.d/messagewall start\" to start messagewall daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/messagewall ]; then
                /etc/rc.d/init.d/messagewall stop >&2
        fi
        /sbin/chkconfig --del messagewall
fi

%files
%defattr(644,root,root,755)
%doc README doc/draft-sasl-login.txt profiles
%attr(755,root,root) %{_bindir}/messagewall*
%attr(755,root,root) %{_libdir}/lib*.so
%dir %{_sysconfdir}/mwall
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mwall/*
%attr(754,root,root) /etc/rc.d/init.d/messagewall
%{_mandir}/man[15]/messagewall*
