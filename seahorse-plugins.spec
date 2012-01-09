Name:		seahorse-plugins
Version:	2.28.1
Release:	2%{?dist}
Summary:	Plugins and utilities for encryption in GNOME
Group:		User Interface/Desktops
License:	GPLv2+ and GFDL
URL:		http://projects.gnome.org/seahorse/
Source:		http://download.gnome.org/sources/seahorse-plugins/2.28/%{name}-%{version}.tar.bz2
Source1:	seahorse-agent.sh

# https://bugzilla.gnome.org/show_bug.cgi?id=579738
Patch0:		seahorse-agent-uninit.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  intltool
BuildRequires:  gettext-devel
BuildRequires:  gnome-doc-utils
BuildRequires:  seahorse
BuildRequires:  pkgconfig
BuildRequires:  libglade2-devel
BuildRequires:  GConf2-devel
BuildRequires:  gtk2-devel
BuildRequires:  gnupg2
BuildRequires:  gpgme-devel
BuildRequires:  nautilus-devel
BuildRequires:  gnome-keyring-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  seahorse-devel
BuildRequires:  libxml2-devel
# epiphany extension hasn't been ported to webkit yet
#BuildRequires:  gecko-devel-unstable
#BuildRequires:  epiphany-devel
BuildRequires:  gedit-devel
BuildRequires:  gnome-panel-devel
BuildRequires:  libnotify-devel
BuildRequires:  evolution-data-server-devel
BuildRequires:  autoconf, automake, libtool, gettext-devel, intltool

Requires: seahorse >= 2.23.6
Requires: gedit
# Requires: epiphany
Requires: GConf2
Requires: shared-mime-info

Requires(post): scrollkeeper
Requires(post): shared-mime-info
Requires(post): GConf2

Requires(pre): GConf2

Requires(preun): GConf2

Requires(postun): scrollkeeper
Requires(postun): shared-mime-info
Requires(postun): GConf2

%description
The plugins and utilities in this package integrate seahorse into
the GNOME desktop environment and allow users to perform operations
from applications like nautilus or gedit.

%prep
%setup -q
%patch0 -p1 -b .uninit

autoreconf -i -f

# cleanup permissions for files that go into debuginfo
find . -type f -name "*.c" -exec chmod a-x {} ';'

%build
GNUPG=/usr/bin/gpg2 ; export GNUPG ; %configure --disable-update-mime-database --disable-epiphany
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

mkdir -p $RPM_BUILD_ROOT/etc/X11/xinit/xinitrc.d/
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT/etc/X11/xinit/xinitrc.d/seahorse-agent.sh

desktop-file-install 					\
	--vendor seahorse 				\
	--delete-original 				\
	--dir $RPM_BUILD_ROOT%{_datadir}/applications	\
	$RPM_BUILD_ROOT%{_datadir}/applications/*

find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name "*.a" -exec rm -f {} ';'

%find_lang %{name} --with-gnome --all-name

# this is just a leftover from the split, the seahorse-plugins docs
# don't use any screenshots atm
rm -rf $RPM_BUILD_ROOT/%{_datadir}/gnome/help/seahorse-plugins/*/figures

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q
update-mime-database %{_datadir}/mime >& /dev/null
update-desktop-database -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule 				\
	%{_sysconfdir}/gconf/schemas/seahorse-plugins.schemas 	\
	%{_sysconfdir}/gconf/schemas/seahorse-gedit.schemas 	\
	>& /dev/null || :
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
   %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  for f in seahorse.schemas seahorse-plugins.schemas seahorse-gedit.schemas; do
    if [ -f %{_sysconfdir}/gconf/schemas/$f ]; then
      gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/$f >& /dev/null || :
    fi
  done
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule 			\
	%{_sysconfdir}/gconf/schemas/seahorse-plugins.schemas 	\
	%{_sysconfdir}/gconf/schemas/seahorse-gedit.schemas 	\
	>& /dev/null || :
fi

%postun
scrollkeeper-update -q
update-desktop-database -q
update-mime-database %{_datadir}/mime >& /dev/null
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
   %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING NEWS README
%{_sysconfdir}/X11/xinit/xinitrc.d/seahorse-agent.sh
%{_sysconfdir}/gconf/schemas/seahorse-plugins.schemas
%{_sysconfdir}/gconf/schemas/seahorse-gedit.schemas
%{_bindir}/seahorse-agent
%{_bindir}/seahorse-preferences
%{_bindir}/seahorse-tool
%{_libdir}/bonobo/servers/GNOME_SeahorseApplet.server
%{_libdir}/seahorse/seahorse-applet
%{_datadir}/gnome-2.0/ui/GNOME_SeahorseApplet.xml
%{_datadir}/applications/seahorse-pgp-encrypted.desktop
%{_datadir}/applications/seahorse-pgp-keys.desktop
%{_datadir}/applications/seahorse-pgp-preferences.desktop
%{_datadir}/applications/seahorse-pgp-signature.desktop
%{_datadir}/mime/packages/seahorse.xml
%{_datadir}/seahorse-plugins
%{_mandir}/man1/seahorse-agent.1.gz
%{_mandir}/man1/seahorse-tool.1.gz
%{_datadir}/pixmaps/seahorse-applet.svg
%{_datadir}/pixmaps/seahorse-plugins
%{_datadir}/icons/hicolor/48x48/apps/seahorse-applet.png
%{_datadir}/icons/hicolor/scalable/apps/seahorse-applet.svg

# gedit plugin
%dir %{_libdir}/gedit-2
%dir %{_libdir}/gedit-2/plugins
%{_libdir}/gedit-2/plugins/libseahorse-pgp.so
%{_libdir}/gedit-2/plugins/seahorse-pgp.gedit-plugin

# nautilus extension
%dir %{_libdir}/nautilus/extensions-2.0
%{_libdir}/nautilus/extensions-2.0/libnautilus-seahorse.so

# epiphany extension
#%dir %{_libdir}/epiphany
#%dir %{_libdir}/epiphany/2.27
#%dir %{_libdir}/epiphany/2.27/extensions
#%{_libdir}/epiphany/2.27/extensions/libseahorseextension.so
#%{_libdir}/epiphany/2.27/extensions/seahorse.ephy-extension

%changelog
* Mon Nov  9 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-2
- Don't call problematic functions in an atexit handler,
  since this can lead to segfaults at session end (#524415)

* Mon Oct 19 2009 Tomas Bzatek <tbzatek@redhat.com> 2.28.1-1
- Update to 2.28.1

* Wed Oct  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Implement GETINFO to make seahorse-agent work with gnupg >= 2.0.12

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Sep  9 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.1-4
- Drop dependencies on applications

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sat Jul 18 2009 Matthias Clasen <mclasen@redhat.com> 2.27.1-2
- Temporarily drop epiphany extension

* Mon May  4 2009 Tomas Bzatek <tbzatek@redhat.com> 2.27.1-1
- Update to 2.27.1

* Mon Apr 27 2009 Christopher Aillon <caillon@redhat.com> - 2.26.1-3
- Rebuild against newer gecko

* Wed Apr 22 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-2
- Make seahorse-agent clean up its tempdir

* Mon Apr 13 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/seahorse-plugins/2.26/seahorse-plugins-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Tue Mar  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Thu Feb 26 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.90-3
- Fix file list

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.90-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb  4 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Mon Dec 22 2008 Tomas Bzatek <tbzatek@redhat.com> 2.25.3-1
- Update to 2.25.3

* Fri Dec 12 2008 Matthias Clasen <mclasen@redhat.com> 2.25.1-3
- Call update-desktop-database in %%post (#473680)

* Mon Dec  8 2008 Matthias Clasen <mclasen@redhat.com> 2.25.1-2
- Own some directories (#474040)

* Thu Nov 13 2008 Matthias Clasen <mclasen@redhat.com> 2.25.1-1
- Update to 2.25.1

* Sun Oct 19 2008 Matthias Clasen <mclasen@redhat.com> 2.24.1-2
- Update to 2.24.1

* Thu Oct  9 2008 Matthias Clasen <mclasen@redhat.com> 2.24.0-4
- Save some space

* Wed Oct  1 2008 Matthias Clasen <mclasen@redhat.com> 2.24.0-3
- Fix the build

* Sun Sep 21 2008 Matthias Clasen <mclasen@redhat.com> 2.24.0-2
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> 2.23.92-1
- Update to 2.23.92

* Thu Sep  4 2008 Matthias Clasen <mclasen@redhat.com> 2.23.91-1
- Update to 2.23.91

* Sun Aug 24 2008 Matthias Clasen <mclasen@redhat.com> 2.23.6-2
- Brutally fix some file conflicts with the main seahorse package

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> 2.23.6-1
- Initial packaging
