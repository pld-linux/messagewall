Summary:	An SMTP proxy with lots of features
Summary(pl.UTF-8):   Rozbudowany serwer proxy dla SMTP
Name:		messagewall
Version:	1.0.8
Release:	0.3
License:	GPL
Group:		Networking
Source0:	http://messagewall.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	c8bb5538b4f004b56ba680d50c549b8f
Source3:	%{name}.init
Patch0:		%{name}-rfc_violation.patch
URL:		http://messagewall.org/
BuildRequires:	firedns-devel >= 0.1.30
BuildRequires:	firestring-devel >= 0.1.23
BuildRequires:	openssl-devel >= 0.9.7d
Requires:	rc-scripts
Requires(post,preun):/sbin/chkconfig
Requires:	firedns >= 0.1.30
Requires:	firestring >= 0.1.23
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

%description -l pl.UTF-8
MessageWall to serwer proxy dla SMTP opublikowany jako wolne
oprogramowanie. Jego miejsce znajduje się pomiędzy twoim serwerem
pocztowym a światem, a jego zadanie to utrzymać z dala wirusy, spam
oraz zarządzać uprawnieniami (relaying). Odróżniającym czynnikiem od
wielu innych usług tego typu, jest to, że oferuje swobodną
konfigurację na poziomie każdego adresu email. MessageWall stosuje
system oceniania pozwalający na odrzucaniu wiadomości na podstawie
szeregu reguł z różnymi wagami i tagujący wiadomość w nagłówku, jeśli
poziom oceny do odrzucenia nie zostanie osiągnięty.

MessageWall wspiera także zaawansowane techniki autentykacji: adres
źródłowy, SMTP AUTH PLAIN lub LOGIN, jak również sesje SSL/TLS od
klientów oraz do właściwego serwera poczty.

MessageWall pobiera reguły filtrowania z profili. Plik konfiguracyjny
definiuje profil domyślny, a dodatkowy plik określa adresy i domeny,
do których należy stosować profil inny niż domyślny. Każdy profil
zawiera szereg reguł dot. filtracji wiadomości.

%prep
%setup -q -n %{name}
%patch0 -p0

%build
# note: configure script is not autoconf-generated
export CC="%{__cc}"
export CFLAGS="%{rpmcflags}"
# FIXME this truncates firemake.cflags
# FIXME file is truncated before it's contents can be cat
echo "`cat firemake.cflags` -I/usr/include/openssl" >firemake.cflags
export CONFDIR=%{_sysconfdir}/mwall
./configure

%{__make} \
	PREFIX=%{_prefix}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/mwall,/etc/rc.d/init.d}

%{__make} install \
	PREFIX=$RPM_BUILD_ROOT%{_prefix} \
	MANDIR=$RPM_BUILD_ROOT%{_mandir} \
	CONFDIR=$RPM_BUILD_ROOT%{_sysconfdir}/mwall \
	INSTALL_USER="`id -u`" \
	INSTALL_GROUP="`id -g`"

#install conf/messagewall.conf $RPM_BUILD_ROOT%{_sysconfdir}/mwall
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/messagewall

# spaces in filenames are ugly and compress-doc doesn't like them
for f in Light Medium Strong ; do
	mv -f profiles/${f}\ Plus profiles/${f}_Plus
done

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
%dir %{_sysconfdir}/mwall
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mwall/*
%attr(754,root,root) /etc/rc.d/init.d/messagewall
%{_mandir}/man[15]/messagewall*
