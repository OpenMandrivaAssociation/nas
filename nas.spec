%define major 2
%define libname %mklibname audio %{major}
%define devname %mklibname audio -d
%define statname %mklibname audio -s -d

Summary:	Network Audio System
Name:		nas
Version:	1.9.2
Release:	13
License:	Public Domain
Group:		System/Servers
URL:		http://radscan.com/nas.html
Source0:	http://nas.codebrilliance.com/nas/%{name}-%{version}.src.tar.gz
Source1:	nasd.init
Source2:	nasd.sysconfig
Patch0:		nas-1.9.2-fix-str-fmt.patch
Patch1:		nas-1.9.2-asneeded.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gccmakedep
BuildRequires:	imake
BuildRequires:	rman
BuildRequires:	x11-util-cf-files
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(xaw7)
BuildRequires:	pkgconfig(xt)
Requires(post,preun):	rpm-helper
Provides:	nasd

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

%package -n	%{libname}
Summary:	Libraries needed for nasd
Group:		System/Libraries
Obsoletes:	%{_lib}nas2 < 1.9.2-10

%description -n	%{libname}
Libraries needed for nasd and other programs linked against nasd.

%package -n	%{devname}
Summary:	Development headers and libraries for writing programs using NAS
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}nas-devel < 1.9.2-10

%description -n	%{devname}
This package allows you to develop your own network audio programs.

%package -n	%{statname}
Summary:	NAS static library
Group:		Development/C
Requires:	%{devname} = %{version}
Provides:	%{name}-static-devel = %{version}-%{release}
Obsoletes:	%{_lib}nas-static-devel < 1.9.2-10

%description -n %{statname}
NAS static library.

%prep
%setup -q
%patch0 -p0
%patch1 -p0

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
    CXXDEBUGFLAGS="%{optflags} -w" EXTRA_LDOPTIONS="%ldflags" CC="gcc %ldflags"

%install
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
install -m755 %{SOURCE1} -D %{buildroot}%{_initrddir}/nasd
install -m755 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/sysconfig/nasd

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

%preun
%_preun_service nasd

%postun
%_postun_userdel nasd

%files
%doc FAQ HISTORY README RELEASE TODO
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/nasd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/nasd
%{_mandir}/man[15]/*
%dir %attr(-,nasd,nasd) %{_localstatedir}/lib/nasd
%{_bindir}/*
%{_initrddir}/nasd

%files -n %{libname}
%{_libdir}/libaudio.so.%{major}*
%{_libdir}/X11/AuErrorDB

%files -n %{devname}
%{_libdir}/lib*.so
%{_includedir}/audio
%{_mandir}/man3/*

%files -n %{statname}
%{_libdir}/lib*.a

