%define	name	nas
%define	version 1.9.2
%define	rel		1
%define release		%mkrel %{rel}
%define	lib_name_orig	lib%{name}
%define	lib_major	2
%define	lib_name	%mklibname %{name} %{lib_major}
%define	lib_name_devel	%mklibname %{name} -d
%define	lib_name_static_devel	%mklibname %{name} -s -d

Summary:	Network Audio System
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	Public Domain
Group:		System/Servers
URL:		http://radscan.com/nas.html
Source0:	http://nas.codebrilliance.com/nas/%{name}-%{version}.src.tar.gz
Source1:	nasd.init
Source2:	nasd.sysconfig
Patch0:		nas-1.9.2-fix-str-fmt.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	x11-util-cf-files
BuildRequires:	imake
BuildRequires:	X11-devel
BuildRequires:	rman
BuildRequires:	gccmakedep
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
Provides:	nasd
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
This package contains a network-transparent, client/server audio
system, with a library Key features of the Network Audio System
include:
 - Device-independent audio over the network
 - Lots of audio file and data formats
 - Can store sounds in server for rapid replay
 - Extensive mixing, separating, and manipulation of audio data
 - Simultaneous use of audio devices by multiple applications
 - Use by a growing number of ISVs
 - Small size
 - Free! No obnoxious licensing terms

%description -l	no
Denne pakken inneholder ett netttverkstransparent, klient/server audio
system, med et bibliotek. Nøkkelfinessene til Network Audio Systemm
inkluderer:
 - Enhetsuavhengig lyd over nettverket
 - Masser av audiofiler og dataformater
 - Kan lagre lyder i tjener for kjapp gjenavspilling
 - Utvidet mixing, separering og manipulering av lyddata
 - Samtidig bruk av lydenheter fra flere applikasjoner på en gang
 - Brukt av ett voksende nummer av uavhengige programvareutviklere
 - Liten i størrelse
 - Gratis! Ingen irriterende lisensbetingelser

%package -n	%{lib_name}
Summary:	Libraries needed for nasd
Group:		System/Libraries

%description -n	%{lib_name}
Libraries needed for nasd and other programs linked against nasd.

%package -n	%{lib_name_devel}
Summary:	Development headers and libraries for writing programs using NAS
Group:      Development/C
Requires:   %{lib_name} = %{version}
Provides:   %{lib_name_orig}-devel = %{version}-%{release}
Provides:   %{name}-devel = %{version}-%{release}
Obsoletes:  %{lib_name}-devel

%description -n	%{lib_name_devel}
This package allows you to develop your own network audio programs.

%package -n	%{lib_name_static_devel}
Summary:	NAS static library
Group:		Development/C
Requires:   %{lib_name_devel} = %{version}
Provides:   %{lib_name_orig}-static-devel = %{version}-%{release}
Provides:   %{name}-static-devel = %{version}-%{release}
Provides:	%{name}-static
Obsoletes:	%{lib_name}-static-devel

%description -n %{lib_name_static_devel}
NAS static library.

%prep
%setup -q
%patch0 -p0

%build
for cfgdir in %{_libdir} %{_prefix}/lib %{_datadir}; do
  if [[ -f "$cfgdir/X11/config/Imake.tmpl" ]]; then
    CONFIGDIR="$cfgdir/X11/config"
    break
  fi
done
if [[ -z "$CONFIGDIR" ]]; then
  echo "Error: Imake.tmpl not found, the package won't build."
  exit 1
fi
make Makefiles CONFIGDIR=$CONFIGDIR
%make World CONFIGDIR=$CONFIGDIR \
    WORLDOPTS="-k CDEBUGFLAGS='%{optflags} -D__USE_BSD_SIGNAL' " \
    CXXDEBUGFLAGS="%{optflags} -w" 

%install
rm -rf %{buildroot}
%makeinstall_std \
   BINDIR="%{_bindir}" \
   LIBDIR="%{_libdir}/X11" \
   INCROOT="%{_includedir}" \
   USRLIBDIR="%{_libdir}" \
   SHLIBDIR="%{_libdir}" \
   MANPATH="%{_mandir}" \
   DOCDIR="%{_datadir}/X11/doc" \
   install.man

mv %{buildroot}%{_sysconfdir}/nas/nasd.conf{.eg,}
install -d %{buildroot}%{_localstatedir}/lib/nasd
install -m755 %{SOURCE1} -D $RPM_BUILD_ROOT%{_initrddir}/nasd
install -m755 %{SOURCE2} -D $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/nasd

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd nasd %{_localstatedir}/lib/nasd /bin/true
usermod -G audio nasd

%post
%_post_service nasd

%triggerpostun -- nas <= 1.9-1
#(peroyvind): be sure to remove old socket belonging to root and restart nasd
#             now that it runs under own user
rm -f /tmp/.sockets/audio*
service nasd condrestart

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%preun
%_preun_service nasd

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%postun
%_postun_userdel nasd

%files
%defattr(644,root,root,755)
%doc FAQ HISTORY README RELEASE TODO
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/nasd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/nasd
%{_mandir}/man[15]/*
%dir %attr(-,nasd,nasd) %{_localstatedir}/lib/nasd
%defattr(755,root,root,755)
%{_bindir}/*
%{_initrddir}/nasd

%files -n %{lib_name}
%defattr(755,root,root,755)
%{_libdir}/lib*.so.%{lib_major}*
%defattr(644,root,root,755)
%{_libdir}/X11/AuErrorDB

%files -n %{lib_name_devel}
%defattr(755,root,root,755)
%{_libdir}/lib*.so
%defattr(644,root,root,755)
#{_datadir}/X11/doc/*
%{_includedir}/audio
%{_mandir}/man3/*

%files -n %{lib_name_static_devel}
%defattr(644,root,root,755)
%{_libdir}/lib*.a
