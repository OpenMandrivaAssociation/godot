%bcond_without  server
%bcond_without  templates

%define bits    %{__isa_bits}
%define versuff stable
%define demoversion 3.2-57baf0a

Name:           godot
Version:        3.2.3
Release:        1
Summary:        Multi-platform 2D and 3D game engine with a feature rich editor
Group:          Development/Tools
License:        MIT
URL:            https://godotengine.org
Source0:        https://github.com/godotengine/godot/archive/%{version}-%{versuff}/%{name}-%{version}-%{versuff}.tar.gz
Source1:        https://github.com/godotengine/godot-demo-projects/archive/%{demoversion}/godot-demo-projects-%{version}.tar.gz

BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glu)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(udev)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xinerama)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  scons
Recommends:     %{name}-demos

%if %{with templates}
Recommends:     %{name}-templates-linux%{bits}
%ifarch x86_64
Recommends:     %{name}-templates-linux32
%endif
%endif

%description
Godot is an advanced, feature packed, multi-platform 2D and 3D game engine.
It provides a huge set of common tools, so you can just focus on making
your game without reinventing the wheel.

Godot is completely free and open source under the very permissive MIT
license. No strings attached, no royalties, nothing. Your game is yours,
down to the last line of engine code.

%files
%doc README.md
%{_bindir}/%{name}
%if %{with templates}
%dir %{_libexecdir}/%{name}
%endif
%dir %{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/scalable/apps/%{name}.svg

#----------------------------------------------------------------------

%package        demos
Summary:        Demo projects to learn how to use Godot Engine
BuildArch:      noarch

%description    demos
This package contains the official demo projects to help new users to learn
the features of the game engine.

%files          demos
%{_datadir}/%{name}/demos/

#----------------------------------------------------------------------

%if %{with server}
%package        server
Summary:        Godot headless binary for servers
Group:          Games/Other

%description    server
This package contains the headless binary for the Godot game engine,
particularly suited for running dedicated servers.

%files          server
%{_bindir}/%{name}-server
%endif

#----------------------------------------------------------------------

%package        runner
Summary:        Shared binary to play games developed with the Godot engine
Group:          Games/Other

%description    runner
This package contains a %{bits} bits binary for the Linux X11 platform,
which can be used to run any game developed with the Godot engine simply
by pointing to the location of the game's data package.

%files          runner
%doc README.md
%{_bindir}/%{name}-runner

#----------------------------------------------------------------------

%if %{with templates}
%package        templates-linux%{bits}
Summary:        Godot export templates for Linux %{bits} bits platforms

%description    templates-linux%{bits}
This package contains release and debug export templates for Linux
%{bits} bits platforms to be used with the Godot engine.

To ensure cross-distro portability, these templates link libstdc++
statically. Note however that those binaries would not work on Fedora
due to incompatible OpenSSL versions linked dynamically.
Use the upstream templates (less secure but more portable) if need be.

%files          templates-linux%{bits}
%{_libexecdir}/%{name}/templates/linux_x11_%{bits}_release
%{_libexecdir}/%{name}/templates/linux_x11_%{bits}_debug
%endif

#----------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}-%{versuff} -a1
%autopatch -p1

%build
export BUILD_REVISION="openmandriva"

%define common_flags CCFLAGS="%{optflags}" CFLAGS="%{optflags}" LINKFLAGS="%{ldflags}" builtin_zlib=no
%define other_flags colored=yes platform=x11 freetype=yes openssl=yes png=yes pulseaudio=yes theora=yes udev=yes use_llvm=yes vorbis=yes xml=yes
%define _scons %scons %common_flags CC=%{__cc} CXX=%{__cxx} %other_flags %{?_smp_mflags}

%if %{with server}
# Build headless version of the editor
%_scons platform=server tools=yes target=release_debug unix_global_settings_path=%{_libexecdir}/%{name}
%endif

# Build graphical editor (tools)
%_scons platform=x11 tools=yes target=release_debug unix_global_settings_path=%{_libexecdir}/%{name}

# Build game runner (without tools)
%_scons platform=x11 tools=no target=release
cp bin/%{name}.x11.opt.%{bits}.llvm bin/%{name}.x11.opt.runner.%{bits}.llvm

%if %{with templates}
# Build Linux export templates for the current arch
# (akien) The binaries won't run on Fedora due to their breakage of
# OpenSSL's soname: https://github.com/godotengine/godot/issues/1391
# but I don't want to distribute them statically linked against OpenSSL
%_scons platform=x11 tools=no target=release
%_scons platform=x11 tools=no target=release_debug CCFLAGS= CFLAGS=

# Rename templates
mkdir -p templates
mv bin/%{name}.x11.opt.%{bits}.llvm templates/linux_x11_%{bits}_release
mv bin/%{name}.x11.opt.debug.%{bits}.llvm templates/linux_x11_%{bits}_debug
%endif

%install
install -d %{buildroot}%{_bindir}
install -m755 bin/%{name}.x11.opt.tools.%{bits}.llvm           %{buildroot}%{_bindir}/%{name}
install -m755 bin/%{name}.x11.opt.runner.%{bits}.llvm          %{buildroot}%{_bindir}/%{name}-runner
%if %{with server}
install -m755 bin/%{name}_server.x11.opt.tools.%{bits}.llvm %{buildroot}%{_bindir}/%{name}-server
%endif

%if %{with templates}
install -d %{buildroot}%{_libexecdir}/%{name}/templates
cp -a templates/* %{buildroot}%{_libexecdir}/%{name}/templates/
%endif

install -d %{buildroot}%{_datadir}/%{name}
cp -a godot-demo-projects-%{demoversion} %{buildroot}%{_datadir}/%{name}/demos

install -D -m644 icon.svg \
    %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.svg

install -d %{buildroot}%{_datadir}/applications
cat << EOF > %{buildroot}%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Name=Godot Engine
GenericName=Libre game engine
Comment=Multi-platform 2D and 3D game engine with a feature rich editor
Exec=%{name} -pm
Icon=%{name}
Terminal=false
Type=Application
Categories=Development;IDE;
EOF
