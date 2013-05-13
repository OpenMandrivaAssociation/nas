%define lib_name_orig lib%{name}
%define lib_major 2
%define lib_name %mklibname %{name} %{lib_major}
%define lib_name_devel %mklibname %{name} -d
%define lib_name_static_devel %mklibname %{name} -s -d

Summary:	Network Audio System
Name:		nas
Version:	1.9.2
Release:	9
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
BuildRequires:	x11-util-cf-files
BuildRequires:	imake
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(xaw7)
BuildRequires:	pkgconfig(xt)
BuildRequires:	rman
BuildRequires:	gccmakedep
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
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
Group:		Development/C
Requires:	%{lib_name} = %{version}
Provides:	%{lib_name_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{lib_name}-devel

%description -n	%{lib_name_devel}
This package allows you to develop your own network audio programs.

%package -n	%{lib_name_static_devel}
Summary:	NAS static library
Group:		Development/C
Requires:	%{lib_name_devel} = %{version}
Provides:	%{lib_name_orig}-static-devel = %{version}-%{release}
Provides:	%{name}-static-devel = %{version}-%{release}
Provides:	%{name}-static
Obsoletes:	%{lib_name}-static-devel

%description -n %{lib_name_static_devel}
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


%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1.9.2-6mdv2011.0
+ Revision: 666555
- mass rebuild

* Thu Dec 23 2010 Funda Wang <fwang@mandriva.org> 1.9.2-5mdv2011.0
+ Revision: 623971
- tighten BR

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1.9.2-4mdv2011.0
+ Revision: 606810
- rebuild

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 1.9.2-3mdv2010.1
+ Revision: 521151
- rebuilt for 2010.1

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 1.9.2-2mdv2010.0
+ Revision: 426204
- rebuild

* Wed Mar 18 2009 Emmanuel Andry <eandry@mandriva.org> 1.9.2-1mdv2009.1
+ Revision: 357344
- BR libxp-devel
- diff p0 to fix format not a string literal
- New version 1.9.2

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - fix static devel package dependencies

* Tue Sep 02 2008 Emmanuel Andry <eandry@mandriva.org> 1.9.1-1mdv2009.0
+ Revision: 278773
- New version
- apply devel policy

* Mon Jun 09 2008 Pixel <pixel@mandriva.com> 1.9a-1mdv2009.0
+ Revision: 217193
- do not call ldconfig in %%post/%%postun, it is now handled by filetriggers
- adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Oct 29 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.9a-1mdv2008.1
+ Revision: 103298
- new release: 1.9a

* Sun May 27 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.9-2mdv2008.0
+ Revision: 31731
- service restart should be conditional

* Sat May 26 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.9-1mdv2008.0
+ Revision: 31520
- new release: 2.1
- fix detection of CONFIGDIR
- update init script with LSB tags
- run nasd under own user


* Sun Mar 18 2007 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.8a-3mdv2007.1
+ Revision: 146343
- fix DoS vulnerability (P0)

* Wed Jan 03 2007 Emmanuel Andry <eandry@mandriva.org> 1.8a-2mdv2007.1
+ Revision: 103934
- rebuild for x86_64 (bug #25304)
- rebuild

  + Per Øyvind Karlsen <pkarlsen@mandriva.com>
    - add gccmakedep to buildrequires to fix x86_64 build
    - 1.8a
    - fix permissions of docs in devel package
    - fix executable-marked-as-config-file
      fix no-prereq-on
    - updated to 1.8, add full url to source

  + Gwenole Beauchesne <gbeauchesne@mandriva.com>
    - X11 config files are now in /usr/share/X11/config
    - workaround xorg packaging bugs
    - clean specfile, workaround rpm #%% bugs

  + Nicolas Lécureuil <neoclust@mandriva.org>
    - Fix File list

  + Helio Chissini de Castro <helio@mandriva.com>
    - Fixed sysinit install
    - Uncompress source files ( except original tarball )
    - Add warn that package is hosted at svn
    - Fixed build requires for new xorg
    - import nas-1.7b-5mdv2007.0

* Tue May 23 2006 Helio Chissini de Castro <helio@mandriva.com> 1.7b-5mdk
- Missing rman as a buildrequires

* Tue May 23 2006 Helio Chissini de Castro <helio@mandriva.com> 1.7b-3mdk
- Recompile against new X.org
- Move path to match new X layout
- Move library to proper %%_lib

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.7b-2mdk
- Rebuild

* Fri Jun 10 2005 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.7b-1mdk
- 1.7b
- fix requires
- %%mkrel

* Sat Apr 16 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.7a-1mdk
- 1.7a

* Thu Feb 10 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.7-3mdk
- fix build

* Thu Dec 02 2004 Götz Waschk <waschk@linux-mandrake.com> 1.7-2mdk
- update file list
- fix buildrequires

* Mon Nov 15 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.7-1mdk
- 1.7

* Mon Nov 08 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.6g-1mdk
- 1.6g

* Tue Jun 22 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.6d-1mdk
- 1.6d
- drop redundant requires

* Sat Jun 05 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.6c-2mdk
- rebuild

* Fri Apr 02 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.6c-1mdk
- 1.6c
- drop P2 (merged upstream)

