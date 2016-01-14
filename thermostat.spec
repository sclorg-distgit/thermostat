# Thermostat version
%global major        1
%global minor        2
%global patchlevel   0
# Real OSGi Bundle-Version is 3.6.6.Final
%global netty_bundle_version       3.6.3
%global jcommon_bundle_version     1.0.18
%global jfreechart_bundle_version  1.0.14
# apache-commons-beanutils
%global beanutils_bundle_version   1.8.3
# apache-commons-codec
%global codec_bundle_version       1.8.0
# apache-commons-collections
%global collections_bundle_version 3.2.1
# apache-commons-logging
%global logging_bundle_version     1.1.2
# Real OSGi Bundle-Version is 2.11.3.RELEASE
%global mongo_bundle_version       2.11.3
%global hc_core_bundle_version     4.3.3
%global hc_client_bundle_version   4.3.6
%global gson_bundle_version        2.2.2

# Flag set to 1 if it's an SCL build. 0 otherwise.
%global is_scl_build %( test -n "$(rpm --eval '%{?scl}')" && echo 1 || echo 0)

# Base path to the JDK which will be used in boot scripts
%global jdk_base /usr/lib/jvm/java-1.7.0-openjdk.x86_64

%{?scl:%scl_package thermostat}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

# Global directory definitions
%global system_datadir %{_root_localstatedir}/lib/%{pkg_name}
%global system_cachedir %{_root_localstatedir}/cache/%{pkg_name}
%global system_logdir %{_root_localstatedir}/log/%{pkg_name}
%global system_statedir %{_root_localstatedir}/run/%{pkg_name}
%global system_initrddir %{_root_sysconfdir}/rc.d/init.d/
%global system_sbindir %{_root_sbindir}
%global system_tmpfilesdir %{_root_exec_prefix}/lib/tmpfiles.d
# _root_<foo> don't seem to be defined in non-SCL context.
# Define some vars we use instead in order for the build to work
# for SCL/non-SCL contexts.
%if %{is_scl_build}
  %global system_confdir %{_root_sysconfdir}
  %global system_root_datadir %{_root_datadir}
%else
  %global system_confdir %{_sysconfdir}
  %global system_root_datadir %{_datadir}
%endif
# system java dir definition (non-scl)
%global system_javadir %{system_root_datadir}/java
%global scl_javadir %{_javadir}

# THERMOSTAT_HOME and USER_THERMOSTAT_HOME variables. Note that
# we use USER_THERMOSTAT_HOME only for systemd related setup.
%global thermostat_home %{_datarootdir}/%{pkg_name}
%if %{is_scl_build}
  %global user_thermostat_home %{_scl_root}
%else
  # Prefix is "/" for non-scl
  %global user_thermostat_home /
%endif

# thermostat-webapp specific variables
%if %{is_scl_build}
  %global thermostat_catalina_base %{_datarootdir}/tomcat
%else
  %global thermostat_catalina_base %{_localstatedir}/lib/tomcats/%{pkg_name}
%endif
%global thermostat_tomcat_service_name %{?scl_prefix}%{pkg_name}-tomcat

# Don't generate native library provides for JNI libs. Those aren't
# SCL-ized and might conflict with base RHEL. See RHBZ#1045552
%filter_from_provides /lib.*\.so(.*)$/d
%filter_setup

# Generate automatic requires/provides. This needs to be later in the
# spec file than the provides filter setup above.
%{?thermostat_find_provides_and_requires}

# Uncomment to build from snapshot out of hg.  See also Release and Source0
#%global hgrev cf184d4064b2

Name:       %{?scl_prefix}thermostat
Version:    %{major}.%{minor}.%{patchlevel}
# Release should be higher than el7 builds. Use convention
# 60.X where X is an increasing int. 60 for rhel-6. We use
# 70.X for rhel-7. For some reason we cannot rely on the
# dist tag.
Release:    60.10%{?dist}
Summary:    A monitoring and serviceability tool for OpenJDK
License:    GPLv2+ with exceptions and OFL
URL:        http://icedtea.classpath.org/thermostat/
# This is the source URL to be used for released versions
Source0:    http://icedtea.classpath.org/download/%{pkg_name}/%{pkg_name}-%{version}.tar.gz
# This is the source to be used for hg snapshot versions
#wget -O thermostat-%{hgrev}.tar.bz2 http://icedtea.classpath.org/hg/%{pkg_name}/archive/%{hgrev}.tar.bz2
# This is the source to be used for hg snapshot versions from a release branch
#wget -O thermostat-%{major}.%{minor}-%{hgrev}.tar.bz2 http://icedtea.classpath.org/hg/release/%{pkg_name}-%{major}.${minor}/archive/%{hgrev}.tar.bz2
#Source0:    thermostat-%{major}.%{minor}-%{hgrev}.tar.bz2
# This is _NOT_ suitable for upstream at this point.
# It's very Fedora specific.
Source1:    thermostat-sysconfig
Source2:    thermostat_icon_64px.svg
# SCL only sources
Source3:    scl-thermostat-tomcat-service-sysconfig
Source5:    scl-tomcat-initd.sh
# This is _NOT_ suitable for upstream at this point.
# jfreechart isn't a bundle upstream. Also some httpclient* related bundles
# include transitive deps upstream, which isn't the case in Fedora (i.e. is
# properly done in Fedora)
Patch0:     fix_bundle_loading.patch
# Patch proposed upstream, but was denied.
# See http://icedtea.classpath.org/pipermail/thermostat/2013-October/008602.html
# For now _NOT_ suitable for upstream until felix ships an API only package which
# is 4.3 OSGi spec.
Patch1:     osgi_spec_fixes.patch
# This is _NOT_ suitable for upstream at this point.
# It makes thermostat itself ignore bundle versions put into thermostat's files
# at build-time. Over time versions of bundles may change. For packaged
# thermostat we rely on RPM enforcing a working set of bundle<=>version pairs that
# work. See: http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1591
Patch2:     ignore_bundle_versions.patch
# Not suitable for upstream.  Different OSGi version means some API compat issues.
Patch3:     osgi_api_fixes.patch
# FIXME remove when upstream supports mongodb 2.6 ootb.
Patch4:     mongodb26_setup_changes.patch
# Ditto (command does not work with 2.6)
Patch5:     remove_adduser_command.patch
# FIXME: remove once rebased to >= 1.2.4 Upstream commit:
# http://icedtea.classpath.org/hg/release/thermostat-1.2/rev/0f250b6c47e8
Patch6:     fix_lucene_symbolic_name.patch
# FIXME: remove once rebased to >= 1.2.4, RHBZ#1199581, Upstream commit:
# http://icedtea.classpath.org/hg/release/thermostat-1.2/rev/1cfebde69814
Patch7:     thermostat_setup_ctrl_c.patch
# Set USER_THERMOSTAT_HOME default to ~/.thermostat-1.2 since this allows
# for better data migration from 1.0 Thermostat.
Patch8:     user_thermostat_home_new_default.patch
# jetty provides the javax.servlet API
Patch9:     servlet_api_jar.patch
# Allow 'thermostat web-storage-service' to read configs from
# ~/.thermostat, by using a custom jaas config.
Patch10:    webstorage_service_custom_jaas.patch
# Remove when this lands in a release:
# http://icedtea.classpath.org/hg/thermostat/rev/296194a48778
Patch11:    non_existent_bundle.patch
# Upstream puts passwords in a world-readable location
Patch12:    rhbz1221989.patch

BuildRequires: gnome-keyring-devel
# laf-utils JNI need pkconfig files for gtk2+
BuildRequires: gtk2-devel
# Use tomcat only for web storage
BuildRequires: tomcat6-servlet-2.5-api

# Bootstrap bundles (started via file name)
BuildRequires: rh-java-common-apache-commons-cli
BuildRequires: rh-java-common-jansi
BuildRequires: %{?scl_prefix}jline2 >= 2.10-3

# SCL-carried OSGi bundles
BuildRequires: %{?scl_prefix}jfreechart >= 1.0.14-7
BuildRequires: %{?scl_prefix}jcommon >= 1.0.17-4
BuildRequires: %{?scl_prefix}netty
BuildRequires: %{?scl_prefix}apache-commons-fileupload

# rh-java-common collection dependencies
BuildRequires: rh-java-common-apache-commons-beanutils
BuildRequires: rh-java-common-apache-commons-codec
BuildRequires: rh-java-common-apache-commons-logging
BuildRequires: rh-java-common-felix-framework
BuildRequires: rh-java-common-google-gson
BuildRequires: rh-java-common-httpcomponents-client
BuildRequires: rh-java-common-httpcomponents-core
BuildRequires: rh-java-common-lucene >= 4.8.0
BuildRequires: rh-java-common-lucene-analysis >= 4.8.0
BuildRequires: rh-java-common-maven-local
# thermostat web-storage-service BRs
BuildRequires: rh-java-common-jetty-server
BuildRequires: rh-java-common-jetty-jaas
BuildRequires: rh-java-common-jetty-webapp
# TODO schemas are needed for offline validation of some xml files
# BuildRequires: rh-java-common-jetty-schemas

# maven30 collection dependencies
BuildRequires: maven30-xmvn
BuildRequires: maven30-maven-dependency-plugin
BuildRequires: maven30-maven-surefire-plugin
BuildRequires: maven30-maven-surefire-provider-junit
BuildRequires: maven30-maven-war-plugin
BuildRequires: maven30-maven-clean-plugin
BuildRequires: maven30-maven-assembly-plugin
BuildRequires: maven30-maven-plugin-bundle
BuildRequires: maven30-maven-javadoc-plugin
BuildRequires: maven30-fusesource-pom

# Mongodb Java driver comes from the mongodb collection
BuildRequires: rh-mongodb26
BuildRequires: rh-mongodb26-mongo-java-driver

# The following BR is SCL only
%{?scl:BuildRequires: tomcat6}

# Note: use auto-requires for java packages.
Requires: java-1.7.0-openjdk
Requires: java-1.7.0-openjdk-devel
Requires: gnome-keyring

# Things coming from the mongodb26 collection
Requires: rh-mongodb26
Requires: rh-mongodb26-mongodb
Requires: rh-mongodb26-mongodb-server

# FIXME auto requires not working?  Manual requires for now.
Requires: %{?scl_prefix}jline2
Requires: %{?scl_prefix}jfreechart
Requires: %{?scl_prefix}netty
Requires: rh-java-common-lucene
Requires: rh-java-common-lucene-analysis
Requires: rh-java-common-httpcomponents-client
Requires: rh-java-common-httpcomponents-core
Requires: rh-java-common-google-gson
Requires: rh-java-common-apache-commons-codec
Requires: rh-java-common-felix-framework
Requires: rh-java-common-objectweb-asm5
Requires: rh-java-common-apache-commons-collections
Requires: rh-java-common-apache-commons-logging
Requires: rh-java-common-apache-commons-beanutils
Requires: rh-java-common-jetty-servlet
Requires: rh-java-common-jetty-io
Requires: rh-java-common-jetty-jmx
Requires: rh-java-common-jetty-server
Requires: rh-java-common-jetty-jaas
Requires: rh-java-common-jetty-util
Requires: rh-java-common-jetty-http
Requires: rh-java-common-jetty-webapp
Requires: rh-java-common-jetty-xml
Requires: rh-java-common-jetty-security
Requires: rh-mongodb26-mongo-java-driver

Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%{?scl:Requires: %scl_runtime}

%description
Thermostat is a monitoring and instrumentation tool for the Hotspot JVM,
with support for monitoring multiple JVM instances. The system is made
up of two processes: an Agent, which collects data, and a Client which
allows users to visualize this data. These components communicate via
a MongoDB-based storage layer. . A pluggable agent and gui framework
allows for collection and visualization of performance data beyond that
which is included out of the box.

%package javadoc
Summary:    Javadocs for %{name}
Group:      Documentation

BuildArch:  noarch

%description javadoc
This package contains the API documentation for %{name}

%package webapp
Summary:    Web storage for Thermostat
Requires:   tomcat6
Requires:   %{?scl_prefix}apache-commons-fileupload
Requires:   %{name} = %{version}-%{release}
%{?scl:Requires: %scl_runtime}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig

# FIXME auto requires not working?  Manual requires for now.
Requires: rh-java-common-apache-commons-io
Requires: rh-java-common-google-gson
Requires: rh-java-common-apache-commons-codec
Requires: rh-java-common-felix-framework

BuildArch:  noarch

%description webapp
This package contains the storage endpoint web application
for Thermostat's Web layer.

%prep

%{?scl:scl enable %{scl} maven30 rh-java-common rh-mongodb26 - << "EOF"}

# When Source0 is released version. 
%setup -q -n %{pkg_name}-%{version}
# When Source0 is a snapshot from HEAD.
#%setup -q -n %{pkg_name}-%{hgrev}
# When Source 0 is a snapshot from a release branch.
#%setup -q -n %{pkg_name}-%{major}-%{minor}-%{hgrev}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1

# Fix up artifact names which have different name upstream
#  lucene
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene" vm-heap-analysis/common
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene" vm-heap-analysis/distribution
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene-analyzers-common" vm-heap-analysis/common
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene-analyzers-common" vm-heap-analysis/distribution
%pom_add_dep "org.apache.lucene:lucene-analyzers-common:4.8.0" vm-heap-analysis/common
%pom_add_dep "org.apache.lucene:lucene-analyzers:4.8.0" vm-heap-analysis/distribution
%pom_add_dep "org.apache.lucene:lucene-core:4.8.0" vm-heap-analysis/common
%pom_add_dep "org.apache.lucene:lucene-core:4.8.0" vm-heap-analysis/distribution
#  httpclient
%pom_remove_dep org.apache.httpcomponents:httpclient-osgi web/client
%pom_add_dep org.apache.httpcomponents:httpclient:4.1.2 web/client
%pom_remove_dep org.apache.httpcomponents:httpclient-osgi client/command
%pom_add_dep org.apache.httpcomponents:httpclient:4.1.2 client/command
#  add httpmime dep. this is included in upstreams' strange jar
%pom_add_dep org.apache.httpcomponents:httpmime:4.1.2 web/client
#  httpcore
%pom_remove_dep org.apache.httpcomponents:httpcore-osgi web/client
%pom_add_dep org.apache.httpcomponents:httpcore:4.1.2 web/client
# need jline 2.10 (otherwise this resolves to jline 1)
%pom_xpath_remove "pom:properties/pom:jline.version"
%pom_xpath_inject "pom:properties" "<jline.version>2.10</jline.version>"

# Don't use maven-exec-plugin. We do things manually in order to avoid this
# additional dep. It's used in agent/core/pom.xml and in keyring/pom.xml
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin agent/core
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin keyring
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin laf-utils

# Remove jacoco-coverage plugin (in main pom.xml and web/war/pom.xml)
%pom_remove_plugin org.jacoco:jacoco-maven-plugin
%pom_remove_plugin org.jacoco:jacoco-maven-plugin web/war

# Remove pmd plugin
%pom_remove_plugin org.apache.maven.plugins:maven-pmd-plugin

# Remove m2e's lifecyle plugin
%pom_remove_plugin org.eclipse.m2e:lifecycle-mapping

# Remove license-maven-plugin
%pom_remove_plugin com.mycila:license-maven-plugin

# Disable dev and testing-only modules
%pom_disable_module dev
%pom_disable_module test common
%pom_disable_module integration-tests
%pom_disable_module testutils storage
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils vm-cpu/common
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils vm-profiler/common
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils thread/collector

# Remove depencency on the web archive for web-storage-service we'll make deps
# available manually
%pom_remove_dep "com.redhat.thermostat:thermostat-web-war" web/endpoint-plugin/web-service

# jetty-schemas is not available
%pom_remove_dep org.eclipse.jetty.toolchain:jetty-schemas web/endpoint-plugin/distribution

# Remove system scope and systemPath for com.sun:tools dependencies.
# xmvn complains about those at install time.
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" agent/core
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" common/core
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" thread/collector
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" vm-heap-analysis/command
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" vm-heap-analysis/client-swing
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" vm-heap-analysis/client-core
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" agent/core
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" agent/proxy/common
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope" agent/proxy/server
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" agent/proxy/common
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" agent/proxy/server
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" common/core
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" thread/collector
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" vm-heap-analysis/command
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" vm-heap-analysis/client-swing
%pom_xpath_remove "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath" vm-heap-analysis/client-core

# Don't install the zip files created during the build
%mvn_package com.redhat.thermostat::zip: __noinstall
# Skip automatic installation of the war module.
# We install it manually. Without this "config" %mvn_build -f
# fails. See RHBZ#963838
%mvn_package com.redhat.thermostat:thermostat-web-war __noinstall
# Don't install :thermostat-common-test, it's a test only dep which
# aren't run during the build.
%mvn_package com.redhat.thermostat:thermostat-common-test __noinstall

# These are just upstream build helpers. Don't install them.
%mvn_package com.redhat.thermostat:thermostat-distribution __noinstall
%mvn_package com.redhat.thermostat:thermostat-assembly __noinstall

# The automatic requires generator gets confused by build-deps. We have
# to __noinstall it in order for mvn() requires generation to work.
%mvn_package com.redhat.thermostat:thermostat-build-deps __noinstall

# thermostat-web-server and thermostat-web-endpoint should be part of the
# webapp sub-package webapp
%mvn_package com.redhat.thermostat:thermostat-web-server webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint-plugin" webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint:pom:" webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint-distribution:pom:" webapp

%{?scl:EOF}

%build
%{?scl:scl enable %{scl} maven30 rh-java-common rh-mongodb26 - << "EOF"}
export CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
# Set JAVA_HOME. make uses this
. /usr/share/java-utils/java-functions
set_jvm
export JAVA_HOME

################## Build JNI bits ########################
pushd annotations
  mkdir -p target/classes
  javac -d target/classes \
           src/main/java/com/redhat/thermostat/annotations/Service.java
popd
pushd config
  mkdir -p target/classes
  javac -d target/classes \
        -cp ../annotations/target/classes \
           src/main/java/com/redhat/thermostat/shared/config/NativeLibraryResolver.java \
           src/main/java/com/redhat/thermostat/shared/config/CommonPaths.java \
           src/main/java/com/redhat/thermostat/shared/config/internal/CommonPathsImpl.java \
           src/main/java/com/redhat/thermostat/shared/config/InvalidConfigurationException.java \
           src/main/java/com/redhat/thermostat/shared/locale/Translate.java \
           src/main/java/com/redhat/thermostat/shared/locale/LocalizedString.java \
           src/main/java/com/redhat/thermostat/shared/locale/internal/LocaleResources.java
popd
pushd keyring
  mkdir -p target/classes
  javac -cp ../config/target/classes:../annotations/target/classes \
        -d target/classes \
           src/main/java/com/redhat/thermostat/utils/keyring/Keyring.java \
           src/main/java/com/redhat/thermostat/utils/keyring/KeyringException.java \
           src/main/java/com/redhat/thermostat/utils/keyring/impl/KeyringImpl.java
  make all
popd
pushd agent/core
  mkdir -p target/classes
  javac -cp ../../config/target/classes:../../annotations/target/classes \
        -d target/classes \
         src/main/java/com/redhat/thermostat/agent/utils/hostname/HostName.java \
         src/main/java/com/redhat/thermostat/agent/utils/username/UserNameUtil.java \
         src/main/java/com/redhat/thermostat/agent/utils/username/UserNameLookupException.java \
         src/main/java/com/redhat/thermostat/utils/username/internal/UserNameUtilImpl.java
  make all
popd
pushd laf-utils
  mkdir -p target/classes
  javac -cp ../config/target/classes \
        -d target/classes src/main/java/com/redhat/thermostat/internal/utils/laf/gtk/GTKThemeUtils.java
  make all
popd
################## Build JNI bits (end) ##################

# Make sure install location does not exist
rm -rf %{buildroot}/%{_datarootdir}/java/%{?scl_prefix}%{pkg_name}
# Do the maven compile, skipping tests
%mvn_build -f -- -Dthermostat.home=%{thermostat_home} \
                 -Dthermostat.web.deploy.dir=$(pwd)/webstorage-webapp \
                 -Dthermostat.system.user=thermostat \
                 -Dthermostat.system.group=thermostat \
                 -Dnetty.version=%{netty_bundle_version}.Final \
                 -Dcommons-logging.version=%{logging_bundle_version} \
                 -Dcommons-collections.version=%{collections_bundle_version} \
                 -Dcommons-codec.osgi-version=%{codec_bundle_version} \
                 -Dcommons-beanutils.version=%{beanutils_bundle_version} \
                 -Dgson.version=%{gson_bundle_version} \
                 -Dmongo-driver.osgi-version=%{mongo_bundle_version}.RELEASE \
                 -Dhttpcomponents.core.version=%{hc_core_bundle_version} \
                 -Dhttpcomponents.client.version=%{hc_client_bundle_version} \
                 -Dhttpcomponents.mime.version=%{hc_client_bundle_version} \
                 -Djcommon.osgi.version=%{jcommon_bundle_version} \
                 -Djfreechart.osgi.version=%{jfreechart_bundle_version} \
                 -Dlucene-core.bundle.symbolic-name=org.apache.lucene.core \
                 -Dlucene-analysis.bundle.symbolic-name=org.apache.lucene.analysis \
                 -Dosgi.compendium.bundle.symbolic-name=org.osgi.compendium \
                 -Dosgi.compendium.osgi-version=4.1.0

# the build puts all depdency jars into distribution/target/image/lib as well
mv distribution/target/image/libs/thermostat-*jar .
rm -f distribution/target/image/libs/*jar
mv thermostat-*jar distribution/target/image/libs/

# Need Java 7 in in scripts
sed -i 's|^JAVA=.*|JAVA="%{jdk_base}/bin/java"|' distribution/target/image/bin/thermostat
sed -i 's|^JAVA=.*|JAVA="%{jdk_base}/bin/java"|' distribution/target/image/bin/thermostat-agent-proxy
# Fix path to tools.jar
sed -i 's|^TOOLS_JAR=.*|TOOLS_JAR="%{jdk_base}/lib/tools.jar"|' distribution/target/image/bin/thermostat
sed -i 's|^TOOLS_JAR=.*|TOOLS_JAR="%{jdk_base}/lib/tools.jar"|' distribution/target/image/bin/thermostat-agent-proxy

# Collect a list of filenames which we later use in order to symlink from /usr/share/java
pushd distribution/target/image/libs
for i in *.jar; do
  newFileName=$(echo $i | sed 's/-\([0-9]\+\.\)\+[0-9]\+\(-[a-zA-Z0-9]\+\)\?//')
  # collect original filenames in a file so that we can symlink to them
  # from %{_datadir}/java/%{pkg_name}
  echo "libs/${i}#${newFileName}" >> ../../../symlink-map-filenames
done
popd
pushd distribution/target/image/plugins
for i in $(find -name 'thermostat-*.jar' | sed 's#^./##g'); do
  fname=$(basename $i)
  newFileName=$(echo $fname | sed 's/-\([0-9]\+\.\)\+[0-9]\+\(-[a-zA-Z0-9]\+\)\?//')
  echo "plugins/${i}#${newFileName}" >> ../../../symlink-map-filenames
done
popd
grep -v "thermostat-web-server" distribution/symlink-map-filenames > distribution/symlink-map-filenames-filtered
mv distribution/symlink-map-filenames-filtered distribution/symlink-map-filenames

# clean-up webapp. these are all symlinks to libs in $THERMOSTAT_HOME
# except for thermostat-web-server
pushd webstorage-webapp
rm -rf WEB-INF/lib/*
popd
mv distribution/target/image/webapp/WEB-INF/lib/thermostat-web-server*.jar webstorage-webapp/WEB-INF/lib
%{?scl:EOF}

%install
%{?scl:scl enable maven30 %{scl} - << "EOF"}
#######################################################
# Thermostat core
#######################################################
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{pkg_name}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{system_confdir}/sysconfig
mkdir -p %{buildroot}%{_datarootdir}/java/%{?scl_prefix}%{pkg_name}
# JNI things live there
mkdir -p %{buildroot}%{_libdir}/%{pkg_name}
mkdir -p %{buildroot}%{_jnidir}
# init script live there
mkdir -p %{buildroot}%{system_initrddir}
# Thermostat icon lives there
mkdir -p %{buildroot}%{_datarootdir}/icons/hicolor/scalable/apps
# Thermostat desktop lives there
mkdir -p %{buildroot}%{_datarootdir}/applications

# Dance the xmvn install limbo. This only makes sense if %mvn_build does NOT
# have the '-i' switch.
%mvn_install

# now make xmvn happy, it expects version-less thermostat jars in
# %{_datadir}/java/%{pkg_name}
rm -rf %{buildroot}%{_datarootdir}/java/%{pkg_name}
mkdir -p %{buildroot}%{_datarootdir}/java/%{pkg_name}
for i in $(cat distribution/symlink-map-filenames); do
  s=$(echo $i | cut -d'#' -f1)
  t=$(echo $i | cut -d'#' -f2)
  ln -s %{_datarootdir}/%{pkg_name}/$s %{buildroot}%{_datarootdir}/java/%{pkg_name}/$t
done

pushd distribution/target/image/libs
# JNI jars need to be in %{_jnidir}, we symlink to
# %{_libdir}/%{pkg_name} files. Files are moved to
# %{_libdir}/%{pkg_name} next.
for i in thermostat-keyring-*.jar \
    thermostat-agent-core-*.jar \
    thermostat-laf-utils-*.jar; do
  ln -s %{_libdir}/%{pkg_name}/$i %{buildroot}%{_jnidir}/$i
done
# JNI files are in %{_libdir}
mv thermostat-keyring-*.jar \
   thermostat-agent-core-*.jar \
   thermostat-laf-utils-*.jar \
   %{buildroot}%{_libdir}/%{pkg_name}
# Make native libs executable so that debuginfos get properly
# generated
chmod +x native/*.so
mv native/* %{buildroot}%{_libdir}/%{pkg_name}
popd

# FIXME: Make sure thermostat-storage can be run via some
# system init script

# Move the thermostat desktop file to /usr/share/applications
# This makes "thermostat gui" show up in gnome shell.
cp distribution/target/%{pkg_name}.desktop %{buildroot}%{_datarootdir}/applications/%{pkg_name}.desktop
# Install the SVG icon
cp %{SOURCE2} %{buildroot}%{_datarootdir}/icons/hicolor/scalable/apps/%{pkg_name}.svg


# Install tmpfiles.d config file for /var/run/%{pkg_name}
mkdir -p %{buildroot}%{system_tmpfilesdir}
install -m 0644 distribution/target/tmpfiles.d/%{pkg_name}.conf %{buildroot}%{system_tmpfilesdir}/%{pkg_name}.conf

# Don't want dev setup things
rm distribution/target/image/bin/thermostat-devsetup
rm distribution/target/image/etc/devsetup.input

# move everything else into $THERMOSTAT_HOME
rm -rf distribution/target/image/bin/thermostat.orig
# Don't install webapp twice
rm -rf distribution/target/image/webapp
cp -a distribution/target/image %{buildroot}%{thermostat_home}

# symlink dependencies into the right directory
ln -s /opt/rh/rh-java-common/root/usr/share/java/felix/org.apache.felix.framework.jar %{buildroot}%{thermostat_home}/libs/org.apache.felix.framework.jar
ln -s /opt/rh/rh-java-common/root/usr/lib/java/hawtjni-runtime.jar %{buildroot}%{thermostat_home}/libs/hawtjni-runtime.jar
# All bundles with symbolic_name=version listed in
# $THERMOSTAT_HOME/etc/commands/<command>.properties or any thermostat-plugin.xml file
# need to be symlinked from $THERMOSTAT_HOME/{libs,plugins/<plugin-name>/}
# The following list is that set and will get started by the OSGi framework as
# bundles in an OSGi sense.
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-beanutils.jar %{buildroot}%{thermostat_home}/libs/commons-beanutils.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-cli.jar %{buildroot}%{thermostat_home}/libs/commons-cli.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-collections.jar %{buildroot}%{thermostat_home}/libs/commons-collections.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-logging.jar %{buildroot}%{thermostat_home}/libs/commons-logging.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/google-gson.jar %{buildroot}%{thermostat_home}/libs/gson.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/httpcomponents/httpcore.jar %{buildroot}%{thermostat_home}/libs/httpcomponents-core.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/httpcomponents/httpclient.jar %{buildroot}%{thermostat_home}/libs/httpcomponents-client.jar
# This comes from the mongodb26 collection.
ln -s /opt/rh/rh-mongodb26/root/usr/share/java/mongo-java-driver/mongo.jar %{buildroot}%{thermostat_home}/libs/mongo.jar
# The following deps are packaged as part of the thermostat-scl
ln -s %{scl_javadir}/netty.jar %{buildroot}%{thermostat_home}/libs/netty.jar
ln -s %{scl_javadir}/jfreechart.jar %{buildroot}%{thermostat_home}/libs/jfreechart.jar
ln -s %{scl_javadir}/jcommon.jar %{buildroot}%{thermostat_home}/libs/jcommon.jar
ln -s %{scl_javadir}/jline2/jline.jar %{buildroot}%{thermostat_home}/libs/jline2.jar
# The following are additional downstream specific symlinks for transitive deps
#   see fix_bundle_loading.patch
# some of them have their deps embedded upstream (or whatever is available in the maven repos)
#
# jline2 => jansi
# httpclient => httpmime
# httpclient => commons-codec
ln -s /opt/rh/rh-java-common/root/usr/share/java/jansi.jar %{buildroot}%{thermostat_home}/libs/jansi.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/httpcomponents/httpmime.jar %{buildroot}%{thermostat_home}/libs/httpcomponents-mime.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-codec.jar %{buildroot}%{thermostat_home}/libs/commons-codec.jar

# set up symlinks for vm-heap-analysis
rm %{buildroot}%{thermostat_home}/plugins/vm-heap-analysis/lucene*jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/lucene/lucene-core.jar %{buildroot}%{thermostat_home}/libs/lucene-core.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/lucene/lucene-analyzers-common.jar %{buildroot}%{thermostat_home}/libs/lucene-analyzers.jar

# set up symlinks for vm-profiler plugin
rm %{buildroot}%{thermostat_home}/plugins/vm-profiler/asm*jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/objectweb-asm5/asm-all-5.jar %{buildroot}%{thermostat_home}/libs/asm-all.jar

# set up symlinks for embedded-web-endpoint plugin
rm %{buildroot}%{thermostat_home}/plugins/embedded-web-endpoint/jetty*jar
rm %{buildroot}%{thermostat_home}/plugins/embedded-web-endpoint/javax.servlet*jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/tomcat-servlet-3.0-api.jar %{buildroot}%{thermostat_home}/libs/javax.servlet-3.0-api.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-http.jar %{buildroot}%{thermostat_home}/libs/jetty-http.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-io.jar %{buildroot}%{thermostat_home}/libs/jetty-io.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-jaas.jar %{buildroot}%{thermostat_home}/libs/jetty-jaas.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-security.jar %{buildroot}%{thermostat_home}/libs/jetty-security.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-server.jar %{buildroot}%{thermostat_home}/libs/jetty-server.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-servlet.jar %{buildroot}%{thermostat_home}/libs/jetty-servlet.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-util.jar %{buildroot}%{thermostat_home}/libs/jetty-util.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-webapp.jar %{buildroot}%{thermostat_home}/libs/jetty-webapp.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/jetty/jetty-xml.jar %{buildroot}%{thermostat_home}/libs/jetty-xml.jar

pushd %{buildroot}%{_libdir}/%{pkg_name}
# symlink JNI jars
for i in *.jar; do
  ln -s %{_libdir}/%{pkg_name}/$i \
        %{buildroot}%{thermostat_home}/libs/$i
done
# symlink shared libs
for i in *.so; do
  ln -s %{_libdir}/%{pkg_name}/$i \
        %{buildroot}%{thermostat_home}/libs/native/$i
done
popd

ln -s /usr/lib/jvm/java-1.7.0-openjdk.x86_64/lib/tools.jar \
    %{buildroot}%{thermostat_home}/libs/

# Symlink the thermostat script in /bin
ln -s %{thermostat_home}/bin/thermostat \
    %{buildroot}%{_bindir}/thermostat
ln -s %{_datarootdir}/%{pkg_name}/bin/thermostat-setup \
    %{buildroot}%{_bindir}/thermostat-setup

# create required config directory
mkdir -p %{buildroot}%{thermostat_home}/etc/plugins.d/
# move config files to /etc and symlink stuff under $THERMOSTAT_HOME/etc to it
mv %{buildroot}%{thermostat_home}/etc/* \
   %{buildroot}%{_sysconfdir}/%{pkg_name}
rmdir %{buildroot}%{thermostat_home}/etc
ln -s %{_sysconfdir}/%{pkg_name}/ \
          %{buildroot}%{thermostat_home}/etc

# Install sysconfig file. This is so as to set THERMOSTAT_HOME to
# /usr/share/thermostat rather than ~/.thermostat which the script
# would do.
sed 's#__thermostat_home__#%{thermostat_home}/#g' %{SOURCE1} > thermostat_sysconfig.env
sed -i 's#__user_thermostat_home__#%{thermostat_home}/#g' thermostat_sysconfig.env
cp thermostat_sysconfig.env %{buildroot}%{_sysconfdir}/sysconfig/%{pkg_name}

# Set up directory structure for running thermostat storage/
# thermostat agend via systemd
%{__install} -d -m 0775 %{buildroot}%{system_datadir}
%{__install} -d -m 0775 %{buildroot}%{system_cachedir}
%{__install} -d -m 0775 %{buildroot}%{system_logdir}
%{__install} -d -m 0775 %{buildroot}%{system_statedir}
# Symlink storage/agent directories so that they can be run
# as systemd services. The target directories will have
# appropriate permissions for the thermostat user to allow
# writing.
ln -s %{system_datadir} %{buildroot}%{thermostat_home}/data
ln -s %{system_statedir} %{buildroot}%{thermostat_home}/run
ln -s %{system_logdir} %{buildroot}%{thermostat_home}/logs
ln -s %{system_cachedir} %{buildroot}%{thermostat_home}/cache

#######################################################
# Thermostat web storage webapp
#######################################################
mkdir -p %{buildroot}%{thermostat_catalina_base}/webapps
pushd webstorage-webapp
# Fixup THERMOSTAT_HOME in web.xml
  sed -i '/<param-name>THERMOSTAT_HOME<[/]param-name>/,/<param-value>.*<[/]param-value>/{ s$<param-value>.*</param-value>$<param-value>%{thermostat_home}</param-value>$ }' \
  WEB-INF/web.xml
popd
# create a symlink to webapp from THERMOSTAT_HOME
ln -s %{thermostat_catalina_base}/webapps/%{pkg_name} %{buildroot}%{thermostat_home}/webapp
cp -r webstorage-webapp %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}
# 
# Make xmvn happy. Give it a symlink in %{_datadir}/java/%{pkg_name}
pushd %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
for i in thermostat-*.jar; do
  newFileName=$(echo $i | sed 's/-\([0-9]\+\.\)\+[0-9]\+\(-[a-zA-Z0-9]\+\)\?//')
  ln -s %{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib/$i %{buildroot}%{_datarootdir}/java/%{pkg_name}/$newFileName
done
popd

# Symlink core libs we need. Basically all jars + transitive deps which
# define model classes.
pushd %{buildroot}%{thermostat_home}/libs
for i in thermostat-storage-core*.jar \
         thermostat-common-core*.jar \
         thermostat-storage-mongodb*.jar \
         thermostat-shared-config*.jar \
         thermostat-keyring*.jar \
         thermostat-annotations*.jar \
         thermostat-web-common*.jar; do
  ln -s %{thermostat_home}/libs/$i \
        %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
done
popd
# Symlink plugin libs shipped with core (we need them for the model
# classes)
pushd %{buildroot}%{thermostat_home}/plugins
for i in $(find -name 'thermostat-*common*.jar' -o \
                -name 'thermostat-thread-collector*.jar'); do
   ln -s %{thermostat_home}/plugins/$i \
         %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
done
popd
# Don't need thermostat-thread-client-common jar for webapp
pushd %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
  rm thermostat-thread-client-common*.jar
popd
# Symlink other dependencies
pushd %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-beanutils.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-codec.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-collections.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-io.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/apache-commons-logging.jar
ln -s /opt/rh/rh-java-common/root/usr/share/java/google-gson.jar
# This comes from the mongodb26 collection.
ln -s /opt/rh/rh-mongodb26/root/usr/share/java/mongo-java-driver/mongo.jar
# The following are SCL-ized in our collection
ln -s %{scl_javadir}/apache-commons-fileupload/commons-fileupload.jar apache-commons-fileupload.jar
popd

# Symlink webapp configuration
mv %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/web.auth \
   %{buildroot}%{_sysconfdir}/%{pkg_name}/
ln -s %{_sysconfdir}/%{pkg_name}/web.auth %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/

# We use a custom CATALINA_BASE with core tomcat directories
# symlinked. This allows us to deploy the thermostat webapp
# nicely configured without any configuration required prior
# starting tomcat via a service init script.
sed 's#__catalina_base__#%{thermostat_catalina_base}#g' %{SOURCE3} > tomcat_service_thermostat.txt
sed -i 's#__jaas_config__#%{_sysconfdir}/%{pkg_name}/%{pkg_name}_jaas.conf#g' tomcat_service_thermostat.txt
cp tomcat_service_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
# install the init script
sed 's#__service_name__#%{thermostat_tomcat_service_name}#g' %{SOURCE5} > tomcat_initd.sh
cp tomcat_initd.sh %{buildroot}%{system_initrddir}/%{thermostat_tomcat_service_name}

# Create a symlinked CATALINA_BASE in order to make tomcat deploy
# the scl-ized tomcat web-app.
pushd %{buildroot}/%{thermostat_catalina_base}
  for i in conf lib logs work temp; do
    ln -s %{system_root_datadir}/tomcat6/$i $i
  done
popd
# Make tomcat with custom catalina base happy (not complain about this dir missing)
mkdir -p %{buildroot}/%{_root_localstatedir}/log/%{thermostat_tomcat_service_name}
%{?scl:EOF}

%check
# Perform some sanity checks on paths to JAVA/TOOLS_JAR
# in important boot scripts. See RHBZ#1052992 and
# RHBZ#1053123
TOOLS_JAR="$(grep 'TOOLS_JAR=' %{buildroot}/%{thermostat_home}/bin/thermostat | cut -d= -f2 | cut -d\" -f2)"
test "${TOOLS_JAR}" = "%{jdk_base}/lib/tools.jar"
TOOLS_JAR="$(grep 'TOOLS_JAR=' %{buildroot}/%{thermostat_home}/bin/thermostat-agent-proxy | cut -d= -f2 | cut -d\" -f2)"
test "${TOOLS_JAR}" = "%{jdk_base}/lib/tools.jar"
JAVA="$(grep 'JAVA=' %{buildroot}/%{thermostat_home}/bin/thermostat | cut -d= -f2 | cut -d\" -f2)"
test "${JAVA}" = "%{jdk_base}/bin/java"
JAVA="$(grep 'JAVA=' %{buildroot}/%{thermostat_home}/bin/thermostat-agent-proxy | cut -d= -f2 | cut -d\" -f2)"
test "${JAVA}" = "%{jdk_base}/bin/java"

%pre
# add the thermostat user and group
%{system_sbindir}/groupadd -r thermostat 2>/dev/null || :
%{system_sbindir}/useradd -c "Thermostat" -g thermostat \
    -s /sbin/nologin -r -d %{thermostat_home} thermostat 2>/dev/null || :

%post
# Required for icon cache (i.e. Thermostat icon)
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%post webapp
# install but don't activate
/sbin/chkconfig --add %{thermostat_tomcat_service_name}

%postun
# Required for icon cache (i.e. Thermostat icon)
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &> /dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%preun webapp
if [ $1 = 0 ]; then
    %{system_initrddir}/%{thermostat_tomcat_service_name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{thermostat_tomcat_service_name}
fi

%posttrans
# Required for icon cache (i.e. Thermostat icon)
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f .mfiles
%doc COPYING
%doc LICENSE
%doc README
# Own appropriate files in /etc/ part of them belong to the
# webapp sub-package
%config(noreplace) %dir %{_sysconfdir}/%{pkg_name}
# This file is only used by the systemd service running agent.
# Only root should be able to read/write to it.
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/%{pkg_name}/agent.auth
%config(noreplace) %{_sysconfdir}/%{pkg_name}/agent.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/commands
%config(noreplace) %{_sysconfdir}/%{pkg_name}/db.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/logging.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/plugins.d
%config(noreplace) %{_sysconfdir}/%{pkg_name}/osgi-export.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/ssl.properties
# Required for systemd services
%config(noreplace) %{_sysconfdir}/sysconfig/%{pkg_name}
# thermostat.desktop lives in /usr/share/applications
%{_datadir}/applications/%{pkg_name}.desktop
# thermostat icon
%{_datadir}/icons/hicolor/scalable/apps/%{pkg_name}.svg
%{_datadir}/%{pkg_name}/etc
%{_datadir}/%{pkg_name}/bin
%{_datadir}/%{pkg_name}/libs
%{_datadir}/%{pkg_name}/plugins/host-cpu
%{_datadir}/%{pkg_name}/plugins/host-memory
%{_datadir}/%{pkg_name}/plugins/host-overview
%{_datadir}/%{pkg_name}/plugins/killvm
%{_datadir}/%{pkg_name}/plugins/notes
%{_datadir}/%{pkg_name}/plugins/numa
%{_datadir}/%{pkg_name}/plugins/storage-profile
%{_datadir}/%{pkg_name}/plugins/thread
%{_datadir}/%{pkg_name}/plugins/validate
%{_datadir}/%{pkg_name}/plugins/vm-classstat
%{_datadir}/%{pkg_name}/plugins/vm-cpu
%{_datadir}/%{pkg_name}/plugins/vm-gc
%{_datadir}/%{pkg_name}/plugins/vm-heap-analysis
%{_datadir}/%{pkg_name}/plugins/vm-jmx
%{_datadir}/%{pkg_name}/plugins/vm-memory
%{_datadir}/%{pkg_name}/plugins/vm-overview
%{_datadir}/%{pkg_name}/plugins/vm-profiler
%{_datadir}/%{pkg_name}/cache
%{_datadir}/%{pkg_name}/data
%{_datadir}/%{pkg_name}/logs
%{_datadir}/%{pkg_name}/run
%{_jnidir}/thermostat-*.jar
%{_bindir}/thermostat
%{_bindir}/thermostat-setup
%{_libdir}/%{pkg_name}/libGTKThemeUtils.so
%{_libdir}/%{pkg_name}/libGnomeKeyringWrapper.so
%{_libdir}/%{pkg_name}/libHostNameWrapper.so
%{_libdir}/%{pkg_name}/libUserNameUtilWrapper.so
%{_libdir}/%{pkg_name}/thermostat-agent-core-1.2.0.jar
%{_libdir}/%{pkg_name}/thermostat-keyring-1.2.0.jar
%{_libdir}/%{pkg_name}/thermostat-laf-utils-1.2.0.jar
# FIXME: install or not-to-install agent service running as root?
#        Currently: Don't install.
#%{_unitdir}/%{pkg_name}-agent.service
%{system_tmpfilesdir}/%{pkg_name}.conf
# To these directories get written to when thermostat storage/agent
# run as systemd services
%attr(0770,thermostat,thermostat) %dir %{system_datadir}
%attr(0770,thermostat,thermostat) %dir %{system_cachedir}
%attr(0770,thermostat,thermostat) %dir %{system_logdir}
%attr(0770,thermostat,thermostat) %dir %{system_statedir}
# Own directories we ship libs in. See RHBZ#1057169
%{_javadir}/%{pkg_name}

%files javadoc
%doc LICENSE
%doc COPYING
%{_datarootdir}/javadoc/%{pkg_name}

%files webapp -f .mfiles-webapp
%{thermostat_catalina_base}
%{_datadir}/%{pkg_name}/webapp
%{_datadir}/%{pkg_name}/plugins/embedded-web-endpoint
%config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}_jaas.conf
%config(noreplace) %{_sysconfdir}/%{pkg_name}/web-storage-service.properties
# Those files should be readable by root and tomcat only
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}-users.properties
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}-roles.properties
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/web.auth

%config(noreplace) %{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
# thermostat tomcat init script
%attr(0755,root,root) %{system_initrddir}/%{thermostat_tomcat_service_name}
%attr(0770,tomcat,tomcat) %dir %{_root_localstatedir}/log/%{thermostat_tomcat_service_name}
%config(noreplace) %{_sysconfdir}/%{pkg_name}/thermostat_webstorageservice_jaas.conf

%changelog
* Mon May 18 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1.2.0-60.10
- Read mongodb credentials from separate file.
- Resolves: RHBZ#1222621 (CVE-2015-3201)

* Tue May 05 2015 Omair Majid <omajid@redhat.com> - 1.2.0-60.9
- Require -asm5 to fix dangling symlink
- Resolves: RHBZ#1218276

* Fri Apr 24 2015 Omair Majid <omajid@redhat.com> - 1.2.0-60.8
- Fix warnings printed on startup
- Resolves: RHBZ#1214921

* Thu Apr 23 2015 Omair Majid <omajid@redhat.com> - 1.2.0-60.7
- Fix dangling symlinks for plugins
- Add explicit requires on jetty packages
- Resolves: RHBZ#1194599

* Wed Apr 22 2015 Omair Majid <omajid@redhat.com> - 1.2.0-60.6
- Enable web-storage-service
- Resolves: RHBZ#1194599

* Thu Apr 2 2015 Jon VanAlten <jvanaltj@redhat.com> - 1.2.0-60.5
- Remove redundant symlinks to lucene jars
- Resolves: RHBZ#1193828
- Replace mongodb's deprecated userAdd with userCreate in thermostat-setup
- Resolves: RHBZ#1193837

* Mon Mar 16 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1.2.0-60.4
- Use ~/.thermostat-1.2 as USER_THERMOSTAT_HOME per default.
- Resolves: RHBZ#1201257.

* Mon Mar 16 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1.2.0-60.3
- Don't own webapp files in main package.
- Resolves: RHBZ#1198787.

* Thu Mar 12 2015 Omair Majid <omajid@redhat.com> - 1.2.0-60.2
- Handle Ctrl-C in thermostat-setup gracefully
- Resolves: RHBZ#1199581

* Fri Jan 30 2015 Jon VanAlten <jvanalte@redhat.com> - 1.2.0-60.1
- Update to 1.2.0 version
- Use rh-java-common, maven30, rh-mongodb26 collections for deps as needed.

* Mon Dec 08 2014 Elliott Baron <ebaron@redhat.com> - 1.0.4-60.6
- Add Obsoletes for agent-proxy-common module.
- Resolves: RHBZ#1170141

* Fri Dec 05 2014 Elliott Baron <ebaron@redhat.com> - 1.0.4-60.5
- Remove obsolete config file.
- Resolves: RHBZ#1170141

* Fri Dec 05 2014 Elliott Baron <ebaron@redhat.com> - 1.0.4-60.4
- Clean up remnants of agent-proxy-common module.
- Resolves: RHBZ#1170141

* Wed Dec 03 2014 Elliott Baron <ebaron@redhat.com> - 1.0.4-60.3
- Remove RMI from agent.
- Resolves: RHBZ#1170141

* Tue Jun 24 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.4-60.2
- Fix xmvn symlinked jars.

* Fri Jun 20 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.4-60.1
- Update to latest upstream bugfix release (1.0.4).
- Build using the maven30 collection.
- Use mvn auto requires.

* Fri Feb 14 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.2-1
- Update to latest upstream release.
- Also fixes RHBZ#1045016 (Keyring issue).
- Require exact version of thermostat core in webapp subpackage.
- Resolves: RHBZ#1064987

* Thu Feb 13 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-12
- Apply patch for ping fix.
- Mention OFL in license field.
- Resolves: RHBZ#1061842

* Mon Feb 10 2014 Omair Majid <omajid@redhat.com> - 1.0.0-11
- Update package description
- Resolves: RHBZ#1062746

* Mon Jan 27 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-10
- Own directories in which we ship files in.
- Resolves: RHBZ#1057169

* Wed Jan 15 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-9
- Fix path to java and tools.jar in boot scripts.
- Add sanity check for correct paths in boot scripts
  in check section.
- Resolves: RHBZ#1053123 RHBZ#1052992

* Wed Jan 08 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-8
- Fix web storage endpoint.
- Resolves: RHBZ#1048273

* Mon Dec 23 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-7
- Don't log WARNING if LSB fallback is used for determining
  distro info.
- Resolves: RHBZ#1045003

* Mon Dec 23 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-6
- Don't generate provides for JNI natives.
- Resolves: RHBZ#1045552

* Mon Dec 23 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-5
- Fix FTBFS since osgi()-style provides have been removed from
  SCL-ized deps.
- Resolves: RHBZ#1045550

* Wed Nov 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-4
- Remove left-over *.orig file from patching.

* Wed Nov 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-3
- Fix Requires and properly enable SCL.

* Tue Nov 26 2013 Omair Majid <omajid@redhat.com> - 1.0.0-2
- Fix %preun scriptlet to only stop service on uninstalls

* Tue Nov 26 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-1
- Update to upstream 1.0.0 release.
- Add ignore_bundle_versions.patch. See IcedTea BZ#1591.
- Fix thermostat1-thermostat-storage service. Works now in
  permissive mode.

* Mon Nov 25 2013 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.0-0.1.20131122hgcf184d4064b2
- Update to 1.0.0 pre-release.
- Update fix_bundle_loading.patch.
- Make webapp subpackage noarch.

* Fri Nov 22 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.15.0-3
- Use java-1.7.0-openjdk explicitly in R/BR.

* Tue Nov 19 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.15.0-2
- Fix webapp subpackage.

* Fri Nov 15 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.15.0-1
- Update to latest upstream release.

* Fri Nov 15 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-13
- Fix symlinks in webapp sub-package. 

* Mon Nov 11 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-12
- thermostat1 enable scriptlet does the mongodb24 enablement, so
  don't do it explicitly any longer.

* Thu Nov 07 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-11
- Remove BR on mongodb24-runtime. Should go into the thermostat1
  metapackage instead.

* Wed Nov 06 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-9
- Build against and use SCL-ized deps including mongodb24's
  mongo-java-driver. This means we depend on the mongodb24-1-2
  metapackage.

* Tue Aug 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-8
- Provide tomcat systemd service file + $CATALINA_BASE
  stub with thermostat-webapp.

* Tue Aug 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-7
- Install pom files again.

* Tue Aug 27 2013 Severin Gehwolf <sgehwolf@redhat.com> - 0.9.2-6
- Reenable webapp subpackage.
- Fix symlinks to system (non-scl) jars.

* Mon Aug 19 2013 Omair Majid <omajid@redhat.com> - 0.9.2-5
- Add initial SCL support to package.
- Disable webapp temporarily

* Wed Jun 05 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.9.2-4
- Don't install thermostat-agent.service due to IcedTea BZ#1460.

* Fri May 31 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.9.2-3
- Add thermostat SVG icon.
- Add systemd requires.

* Wed May 29 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.9.2-2
- Fix warning on uninstall.

* Fri May 24 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.9.2-1
- Update to upstream 0.9.2 release.
- With this update, storage/agent systemd services work in
  permissive mode.

* Wed May 22 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.9.0-1
- Update to upstream 0.9.0 release.
- Remove thermostat-client script.
- Fixes RHBZ#966892.

* Tue May 21 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.8.0-0.1.20130521hg97e66ed2e4ae
- Update to 0.8.0 pre-release.
- Install systemd unit files.

* Tue May 21 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-18
- Move require of servlet API to webapp sub-package.

* Mon May 20 2013 Omair Majid <omajid@redhat.com> 0.6.0-17
- COPYING and LICENSE should be included in all packages
- javadoc subpackage should be noarch

* Fri May 17 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-17
- Finish move to new-style mvn packaging.

* Fri May 17 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-16
- More xmvn + proper pom installation packaging progress.

* Fri May 17 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-15
- Require xmvn >= 0.4.2-1.1 in order to be able to skip installation
  of the web archive module.
- More work towards new-style packaging.

* Thu May 16 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-14
- More fixes using pom macros.
- Experiment with new-style packaging. Hit a road-block. Need a
  web archive installer which xmvn doesn't support :(

* Thu May 16 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-13
- Remove one more patch which can be replaced by pom macros.

* Fri Mar 15 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-12
- Remove plugins we don't need via pom macros.
- Add missing BR maven-javadoc-plugin.

* Fri Mar 15 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-11
- Fix webapp so as to allow symlinking deps.
- Add default users for webstorage.

* Fri Mar 15 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-10
- Fixup web.xml in thermostat-webapp.

* Thu Mar 14 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-9
- Fix thermostat-webapp so as to include web-server.jar

* Thu Mar 14 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-8
- Make disable_webservice_cmd.patch smaller (use pom macros instead).
- Remove unwanted files in /usr/share/thermostat which are generated by
  maven.
- Put all config files in /etc and symlink from appropriate places.

* Thu Mar 14 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-7
- Use pom macros instead of patches.

* Wed Mar 13 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-6
- Add webapp subpackage.

* Wed Mar 13 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-5
- Fix NPE on help.
- Fix bundle resolution errors for heap analysis commands.

* Tue Mar 12 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-4
- Fix bundle-loading patch so that all commands depending on
  httpcomponents-*.jars also start httpmime.

* Tue Mar 12 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-3
- Update init-layout-patch (was missing plugins symlink).
- Fix OSGi filter syntax (prevented thermostat gui from booting).

* Mon Mar 11 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.6.0-2
- Disable webservice command.
- Do a tomcat-only build.
- Work around jline2 jar not being there (see RHBZ#919640).

* Fri Mar 8 2013 Jon VanAlten <jon.vanalten@redhat.com> - 0.6.0-1
- Update to upstream 0.6.0 release.
- Also fix RHBZ 914544 (ftbfs)

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.0-0.28.20121123hgd6145521e208
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 0.5.0-0.27.20121123hgd6145521e208
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Jan 7 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.26.20121123hgd6145521e208
- Remove felix-osgi-compendium BR/R since we don't use it (yet).

* Mon Jan 7 2013 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.25.20121123hgd6145521e208
- Fix for RHBZ 891840 (NoSuchMethodError on boot).

* Thu Dec 20 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.24.20121123hgd6145521e208
- Fix broken symlinks in %{_jnidir}. See RHBZ#889187.

* Wed Dec 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.5.0-0.23.20121123hgd6145521e208
- revbump after jnidir change

* Fri Nov 23 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.22.20121123hgd6145521e208
- Update to more recent snapshot.
- New BR maven-war-plugin.

* Fri Nov 23 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.21.20121121hg09c2918d8656
- Require better lucene which has the javax.management
  ImportPackage header.

* Thu Nov 22 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.5.0-0.20.20121121hg09c2918d8656
- Build a first pre-release version of thermostat.
- Includes web layer.

* Thu Nov 15 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-7
- Export JAVA_HOME before calling make.

* Thu Nov 15 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-6
- Set JAVA_HOME via set_jvm.

* Wed Nov 14 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-5
- Don't use maven-exec-plugin for compiling native bits.

* Mon Oct 22 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-4
- Require >= jline2-2.5-7 since it has the import-package fix
  (see RHBZ#868291).

* Mon Oct 22 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-3
- Fix RHBZ#868486
- Debug-infos were not properly generated.
- Do not override CFLAGS/LDFLAGS.

* Fri Oct 19 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-2
- Fix jfreechart.jar symlink name.

* Tue Oct 16 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.4.0-1
- Update to upstream 0.4 release.
- Starts dependencies as bundles.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 19 2012 Severin Gehwolf <sgehwolf@redhat.com> 0.3-2
- Removed now obsolete patch (with jfreechart updated to 1.0.14)
- Added BR

* Thu Jul 12 2012 Omair Majid <omajid@redhat.com> - 0.3-1
- Update to upstream 0.3 release

* Sun May 06 2012 Omair Majid <omajid@redhat.com> - 0.2-0.20120506hg2140a7c81a4b
- Resolve RH813539
- Remove uneeded require on fusesource-pom
- Fix jar to use jline2 instead of jline

* Fri May 04 2012 Omair Majid <omajid@redhat.com> - 0.2-0.20120503hg2140a7c81a4b
- Update to pre-release upstream snapshot

* Mon Feb 13 2012 Omair Majid <omajid@redhat.com> - 0.1-1
- Updated description

* Tue Feb 07 2012 Omair Majid <omajid@redhat.com> - 0.1-1
- Intial package
