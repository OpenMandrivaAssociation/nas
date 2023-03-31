%define major 2
%define libname %mklibname audio %{major}
%define devname %mklibname audio -d
%define _disable_lto 1
%global __requires_exclude ^perl\\(getopts.pl\\)
%define daemon nasd
%global optflags %{optflags} -fcommon

Summary:	Network Audio System
Name:		nas
Version:	1.9.4
Release:	12
License:	Public Domain
Group:		System/Servers
URL:		http://radscan.com/nas.html
Source0:	http://nas.codebrilliance.com/nas/%{name}-%{version}.src.tar.gz
Source1:	nasd.service
Source2:	nasd.sysconfig
Patch0:		nas-1.9.3-Move-AuErrorDB-to-SHAREDIR.patch
Patch1:		nas-1.9.2-asneeded.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gccmakedep
BuildRequires:	imake
BuildRequires:	makedepend
BuildRequires:	rman
BuildRequires:	x11-util-cf-files
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(xaw7)
BuildRequires:	pkgconfig(xt)
BuildRequires:	rpm-helper
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

%prep
%setup -q
%patch0 -p1 -b .move_AuErrorDB

%before_configure
# Update config.sub to support aarch64, bug #926196
sed -i -e '/AC_FUNC_SNPRINTF/d' config/configure.ac
autoreconf -i -f config

%build
xmkmf
# See HISTORY file how to modify CDEBUGFLAGS
make WORLDOPTS='-k CDEBUGFLAGS="%{optflags}" -k EXTRA_LDOPTIONS="%{ldflags}"' %{?_smp_mflags} World


%install
make DESTDIR=$RPM_BUILD_ROOT BINDIR=%{_bindir} INCROOT=%{_includedir} \
  LIBDIR=%{_libdir}/X11  SHLIBDIR=%{_libdir} USRLIBDIR=%{_libdir} \
  MANPATH=%{_mandir} INSTALLFLAGS='-p' EXTRA_LDOPTIONS='%{ldflags}' \
  install install.man

install -p -m644 -D %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/%{daemon}.service
install -p -m644 -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{daemon}

# Rename config file
mv $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/nasd.conf{.eg,}

## unpackaged files
# Remove static libraries
rm -fv $RPM_BUILD_ROOT%{_libdir}/lib*.a
mkdir -p %{buildroot}%{_localstatedir}/lib/nasd


%post
%systemd_post %{daemon}.service

%preun
%systemd_preun %{daemon}.service

%postun
%systemd_postun_with_restart %{daemon}.service

%pre
%_pre_useradd nasd %{_localstatedir}/lib/nasd /bin/true
usermod -G audio nasd

%files
%doc FAQ HISTORY README RELEASE TODO
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/nasd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/nasd
%{_mandir}/man[15]/*
%dir %attr(-,nasd,nasd) %{_localstatedir}/lib/nasd
%{_bindir}/*
%{_unitdir}/nasd.service

%files -n %{libname}
%{_libdir}/libaudio.so.%{major}*
%{_datadir}/X11/AuErrorDB

%files -n %{devname}
%{_libdir}/lib*.so
%{_includedir}/audio
%{_mandir}/man3/*
