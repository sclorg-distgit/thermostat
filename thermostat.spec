# Do not repack jars
%global __jar_repack 0

# Upstream Thermostat version triplet
%global major        1
%global minor        6
%global patchlevel   6

# non_bootstrap_build == 1 means add self-BR so that
# xmvn-subst symlinks correctly
%global non_bootstrap_build 1

%if 0%{?rhel}

%if 0%{?rhel} <= 6
  %global is_rhel_6 1
  %global with_systemd 0
  %global custom_release   60
  %global tomcat_name tomcat6
%else
  %global is_rhel_6 0
  %global with_systemd 1
  %global custom_release   70
  %global tomcat_name tomcat
%endif

%else

%global is_rhel_6 0
%global with_systemd 1
%global custom_release   1

%endif

# Thermostat requires exact versions for bundle dependencies.
# We use those versions to pass to the maven build in order for
# it to set it in relevant files.

%if 0%{?fedora} >= 22

  #########################################
  # Fedora 23 and up
  #########################################

  # Real OSGi Bundle-Version is 3.9.3.Final
  %global netty_bundle_version       3.10.6
  %global jcommon_bundle_version     1.0.23
  %global jfreechart_bundle_version  1.0.19
  # apache-commons-beanutils
  %global beanutils_bundle_version   1.9.3
  # apache-commons-codec
  %global codec_bundle_version       1.10.0
  # apache-commons-collections
  %global collections_bundle_version 3.2.2
  # apache-commons-logging
  %global logging_bundle_version     1.2.0
  %global hc_core_bundle_version     4.4.6
  %global hc_client_bundle_version   4.5.2
  %global gson_bundle_version        2.3.1
  %global mongo_bundle_version       3.2.1
  %global lucene_analysis_core_bsn   org.apache.lucene.analyzers-common
  %global lucene_version             5.5.0
  # The javax.servlet bundle version used by the
  # endpoint plugin: a.k.a web-storage-service
  %global javax_servlet_bundle_version 3.1.0
  %global javax_servlet_bsn            javax.servlet-api
  %global jgraphx_bundle_version       3.6.0
  # xmvn-subst in rawhide and later fedoras support
  # in reactor symlinking. See RHBZ#1226251
  %global xmvn_subst_args              -R %{buildroot} .
  %global jetty_version                9.4.0.M0
  %global tomcat_version               8

%else

  #########################################
  # EL 6 + 7
  #########################################
  # Real OSGi Bundle-Version is 3.6.3.Final
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
  %global hc_core_bundle_version     4.3.3
  %global hc_client_bundle_version   4.3.6
  %global gson_bundle_version        2.2.4
  %global mongo_bundle_version       3.2.1
  %global lucene_analysis_core_bsn   org.apache.lucene.analyzers-common
  %global lucene_version             5.4.1
  # The javax.servlet bundle version used by the
  # endpoint plugin: a.k.a web-storage-service
  # Comming from rh-java-common-tomcat-servlet-XXX-api
  # package.
  %global javax_servlet_bundle_version 3.0.0
  %global javax_servlet_bsn            javax.servlet
  %global jgraphx_bundle_version       3.1.2
  %global xmvn_subst_args              .
  %global jetty_version                9.0.3.v20130506
  %global tomcat_version               7
%endif

# Jansi is used as bootstrap bundle and the
# bootstrap bundle properties file refers to the jar
# with version suffix. See 0001_shared_fix_bundle_loading.patch
%global jansi_version              1.11


# Base path to the JDK which will be used in boot scripts
%global jdk_base /usr/lib/jvm/java

%{?scl:%scl_package thermostat}
%{!?scl:%global pkg_name %{name}}

# Global directory definitions
# _root_<foo> don't seem to be defined in non-SCL context.
# Define some vars we use instead in order for the build to work
# for SCL/non-SCL contexts.
%{?scl:
  %global system_confdir %{_root_sysconfdir}
  %global system_root_datadir %{_root_datadir}
  %global system_tmpfilesdir %{_root_exec_prefix}/lib/tmpfiles.d
  %global system_datadir %{_root_localstatedir}/lib/%{name}
  %global system_cachedir %{_root_localstatedir}/cache/%{name}
  %global system_logdir %{_root_localstatedir}/log/%{name}
  %global system_statedir %{_root_localstatedir}/run/%{name}
  %global system_sbindir %{_root_sbindir}
  %global thermostat_desktop_app_anme "'Thermostat (from SCL)'"

# directories for system user for storage as a systemd service
  %global user_datadir %{_localstatedir}/lib
  %global user_cachedir %{_localstatedir}/cache
  %global user_logdir %{_localstatedir}/log
  %global user_statedir %{_localstatedir}/run
%if 0%{?is_rhel_6}
  %global system_initrddir %{_root_sysconfdir}/rc.d/init.d/
%endif
}
# not SCL
%{!?scl:
  %global system_confdir %{_sysconfdir}
  %global system_root_datadir %{_datadir}
  %global system_tmpfilesdir %{_tmpfilesdir}
  %global system_datadir %{_localstatedir}/lib/%{name}
  %global system_cachedir %{_localstatedir}/cache/%{name}
  %global system_logdir %{_localstatedir}/log/%{name}
  %global system_statedir %{_localstatedir}/run/%{name}
  %global thermostat_desktop_app_anme Thermostat
}

# Some Maven coordinates mismatch due to compat versioning.
%{!?scl:
%global object_web_asm_maven_coords org.ow2.asm:asm-all
%global lucene_core_coords          org.apache.lucene:lucene-core
%global lucene_analyzers_coords     org.apache.lucene:lucene-analyzers
%global netty_maven_coords          io.netty:netty:%{netty_bundle_version}
}
%{?scl:
# objectweb-asm is objectweb-asm5 in SCL
%global object_web_asm_maven_coords org.ow2.asm:asm-all:5
# netty coordinates are org.jboss.netty:netty in SCL
%global netty_maven_coords org.jboss.netty:netty
%global lucene_core_coords          org.apache.lucene:lucene-core:5
%global lucene_analyzers_coords     org.apache.lucene:lucene-analyzers:5
}


# THERMOSTAT_HOME and USER_THERMOSTAT_HOME variables. Note that
# we use USER_THERMOSTAT_HOME only for systemd related setup.
%global thermostat_home %{_datarootdir}/%{pkg_name}
%{?scl:
# /opt/rh/rh-thermostat16/root
  %global user_thermostat_home %{_scl_root}
}
# not SCL
%{!?scl:
  # Prefix is "/" for non-scl
  %global user_thermostat_home /
}

# thermostat-webapp specific variables
%{?scl:
  %global thermostat_catalina_base %{_datarootdir}/tomcat
}
# not SCL
%{!?scl:
  %global thermostat_catalina_base %{_localstatedir}/lib/tomcats/%{pkg_name}
}
%global system_catalina_home %{system_root_datadir}/%{tomcat_name}
# The port tomcat will be listening on
%global thermostat_catalina_port 8999
%global thermostat_tomcat_service_name %{?scl_prefix}%{pkg_name}-tomcat

# Don't generate native library provides for JNI libs. Those aren't
# SCL-ized and might conflict with base RHEL. See RHBZ#1045552
%{?scl:
  %if 0%{?is_rhel_6}
    %filter_from_provides /lib.*\.so(.*)$/d
    %filter_setup
  %else
    %global __provides_exclude_from ^%{_libdir}/thermostat/.*|%{thermostat_home}/libs/native/.*$
  %endif
}

%if 0%{?rhel}
  # Use java common's requires/provides generator
  %{?java_common_find_provides_and_requires}
%endif

# Uncomment to build from snapshot out of hg.  See also Release and Source0
#%%global hgrev b7c6db90e034

Name:       %{?scl_prefix}thermostat
Version:    %{major}.%{minor}.%{patchlevel}
# If building from snapshot out of hg, uncomment and adjust below value as appropriate
#Release:    0.1.20131122hg%{hgrev}%{?dist}
Release:    %{custom_release}.3%{?dist}
Summary:    A monitoring and serviceability tool for OpenJDK
License:    GPLv2+ with exceptions and OFL
URL:        http://icedtea.classpath.org/thermostat/
# This is the source URL to be used for released versions
Source0:    http://icedtea.classpath.org/download/%{pkg_name}/%{pkg_name}-%{version}.tar.gz
# This is the source to be used for hg snapshot versions from HEAD
#wget -O thermostat-%{hgrev}.tar.bz2 http://icedtea.classpath.org/hg/%{pkg_name}/archive/%{hgrev}.tar.bz2
#Source0:    thermostat-%{hgrev}.tar.bz2
# This is the source to be used for hg snapshot versions from a release branch
#wget -O thermostat-%{major}.%{minor}-%{hgrev}.tar.bz2 http://icedtea.classpath.org/hg/release/%{pkg_name}-%{major}.${minor}/archive/%{hgrev}.tar.bz2
#Source0:    thermostat-%{major}.%{minor}-%{hgrev}.tar.bz2
# This is _NOT_ suitable for upstream at this point.
# It's very Fedora/SCL specific.
Source1:    thermostat-sysconfig
Source3:    scl-thermostat-tomcat-service-sysconfig
Source4:    fedora-thermostatrc
Source5:    scl-tomcat-initd.sh
Source6:    scl-tomcat-systemd.service

# This is _NOT_ suitable for upstream at this point.
# jfreechart isn't a bundle upstream. Also some httpclient* related bundles
# include transitive deps upstream, which isn't the case in Fedora (i.e. is
# properly done in Fedora)
Patch1:     0001_shared_fix_bundle_loading.patch
# Patch proposed upstream, but was denied.
# See http://icedtea.classpath.org/pipermail/thermostat/2013-October/008602.html
# For now _NOT_ suitable for upstream until felix ships an API only package which
# is 4.3 OSGi spec.
Patch2:     0002_shared_osgi_spec_fixes.patch

%{?scl:
%if 0%{?non_bootstrap_build}
# Work-around xmvn-subst limitation
BuildRequires: %{?scl_prefix}thermostat-webapp = %{version}
%endif
}

# RHEL 6 does not have virtual provides java-devel >= 1.7
%if 0%{?is_rhel_6}
BuildRequires: java-1.7.0-openjdk-devel
%else
BuildRequires: java-devel >= 1:1.7.0
%endif
BuildRequires: %{?scl_prefix_java_common}javapackages-tools
BuildRequires: %{?scl_prefix_maven}maven-local
BuildRequires: %{?scl_prefix_maven}maven-dependency-plugin
BuildRequires: %{?scl_prefix_maven}maven-shade-plugin
BuildRequires: %{?scl_prefix_maven}maven-surefire-plugin
BuildRequires: %{?scl_prefix_maven}maven-war-plugin
BuildRequires: %{?scl_prefix_maven}maven-clean-plugin
BuildRequires: %{?scl_prefix_maven}maven-assembly-plugin
BuildRequires: %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires: %{?scl_prefix_maven}maven-javadoc-plugin
BuildRequires: %{?scl_prefix_maven}maven-antrun-plugin
# Archetype maven plugins not available in SCL
%{!?scl:
BuildRequires: %{?scl_prefix_maven}maven-archetype-packaging
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-archetype-plugin)
}
%if 0%{?is_rhel_6}
BuildRequires: gnome-keyring-devel
%else
# Use libsecret on Fedora
%{!?scl:
BuildRequires: libsecret-devel
}
%{?scl:
BuildRequires: libgnome-keyring-devel
}
%endif
# Keyring JNI uses autotools
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
# laf-utils JNI need pkconfig files for gtk2+
BuildRequires: gtk2-devel
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.felix:org.apache.felix.framework)
BuildRequires: %{?scl_prefix_maven}mvn(org.fusesource:fusesource-pom:pom:)
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.commons:commons-cli)
BuildRequires: %{?scl_prefix_java_common}mvn(jline:jline)
BuildRequires: %{?scl_prefix_java_common}mvn(org.fusesource.jansi:jansi)
BuildRequires: %{?scl_prefix_java_common}mvn(%{lucene_core_coords})
BuildRequires: %{?scl_prefix_java_common}mvn(%{lucene_analyzers_coords})
BuildRequires: %{?scl_prefix_java_common}mvn(com.google.code.gson:gson)
BuildRequires: %{?scl_prefix}mvn(org.jfree:jfreechart)
BuildRequires: %{?scl_prefix}mvn(org.jfree:jcommon)
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.commons:commons-beanutils)
BuildRequires: %{?scl_prefix_mongodb}mvn(org.mongodb:mongo-java-driver)
# Change to netty 4 once RHBZ#1053619 is
# resolved.
# The version number in mvn() means it's a compat package.
BuildRequires: %{?scl_prefix}mvn(%{netty_maven_coords})

# BRs for webapp sub-package
BuildRequires: %{?tomcat_name}

BuildRequires: %{?scl_prefix_java_common}mvn(javax.servlet:servlet-api) >= 2.5
BuildRequires: %{?scl_prefix_java_common}mvn(commons-fileupload:commons-fileupload)

# thermostat web-storage-service BRs
BuildRequires: %{?scl_prefix_java_common}mvn(org.eclipse.jetty:jetty-server)
BuildRequires: %{?scl_prefix_java_common}mvn(org.eclipse.jetty:jetty-jaas)
BuildRequires: %{?scl_prefix_java_common}mvn(org.eclipse.jetty:jetty-webapp)
# FIXME: jetty-schemas not available in SCLs
%if 0%{?fedora}
BuildRequires: mvn(org.eclipse.jetty.toolchain:jetty-schemas)
%endif

###################################################
# The following BRs are specified via osgi's
# symbolic name. This is to ensure exact versions
# as specified in thermostat's bundle list has
# a chance of working at runtime.
###################################################
# 1.0.14-7 has OSGi metadata and itext dep fix
BuildRequires: %{?scl_prefix}osgi(org.jfree.jfreechart) = %{jfreechart_bundle_version}
# 1.0.17-4 has OSGi metadata
BuildRequires: %{?scl_prefix}osgi(org.jfree.jcommon) = %{jcommon_bundle_version}
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.commons.logging) = %{logging_bundle_version}
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.commons.beanutils) = %{beanutils_bundle_version}
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.commons.codec) = %{codec_bundle_version}
BuildRequires: %{?scl_prefix_mongodb}osgi(org.mongodb.mongo-java-driver) = %{mongo_bundle_version}
# Netty osgi provides are not there in SCL
%{!?scl:
BuildRequires: %{?scl_prefix}osgi(org.jboss.netty) = %{netty_bundle_version}
}
BuildRequires: %{?scl_prefix_java_common}osgi(com.google.gson) = %{gson_bundle_version}
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpcore) = %{hc_core_bundle_version}
# httpmime comes from httpcomponents-client just like httpclient itself
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpclient) = %{hc_client_bundle_version}
BuildRequires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpmime) = %{hc_client_bundle_version}
# The thread plugin needs this for visualizing thread deadlocks
BuildRequires: %{?scl_prefix}osgi(com.mxgraph) = %{jgraphx_bundle_version}
# The web endpoint plugin gets this bundle baked into the bundles list.
BuildRequires: %{?scl_prefix_java_common}osgi(%{javax_servlet_bsn}) = %{javax_servlet_bundle_version}
BuildRequires: %{?scl_prefix_java_common}mvn(%{object_web_asm_maven_coords}) >= 5

%{?!scl:
Requires: javapackages-tools
Requires: java-devel >= 1:1.8.0
}
%{?scl:
Requires: %{?scl_prefix}runtime
%if 0%{?is_rhel_6}
# java-devel-openjdk is introduced in RHEL 6.8
# use java7-devel-openjdk for 6.7 and below
Requires: java7-devel-openjdk >= 1:1.7
%else
Requires: java-devel-openjdk >= 1:1.7
%endif
}
# Only require mongodb-server on arches where it's available
%ifarch %{arm} %{ix86} x86_64
Requires: %{?scl_prefix_mongodb}mongodb-server
# Fedora's thermostat-setup uses mongo directly
Requires: %{?scl_prefix_mongodb}mongodb
%endif
%if 0%{?is_rhel_6}
Requires: gnome-keyring
%else
# Use libsecret on Fedora
%{?!scl:
Requires: libsecret
}
%{?scl:
Requires: libgnome-keyring
}
%endif
%if 0%{?is_rhel_6}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif
# Sanity requires for needed OSGi bundles.
Requires: %{?scl_prefix}osgi(org.jfree.jfreechart) >= %{jfreechart_bundle_version}
Requires: %{?scl_prefix}osgi(org.jfree.jcommon) >= %{jcommon_bundle_version}
Requires: %{?scl_prefix_java_common}osgi(org.apache.commons.logging) >= %{logging_bundle_version}
Requires: %{?scl_prefix_java_common}osgi(org.apache.commons.beanutils) >= %{beanutils_bundle_version}
Requires: %{?scl_prefix_java_common}osgi(org.apache.commons.codec) >= %{codec_bundle_version}
# FIXME: switch back to mongodb prefix once 2.13.2 is available in
# the mongodb collection.
Requires: %{?scl_prefix_mongodb}osgi(org.mongodb.mongo-java-driver) >= %{mongo_bundle_version}
# Netty osgi provides is not there in SCL
%{!?scl:
Requires: %{?scl_prefix}osgi(org.jboss.netty) = %{netty_bundle_version}
}
Requires: %{?scl_prefix_java_common}osgi(com.google.gson) >= %{gson_bundle_version}
Requires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpcore) >= %{hc_core_bundle_version}
# httpmime comes from httpcomponents-client just like httpclient itself
Requires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpclient) >= %{hc_client_bundle_version}
Requires: %{?scl_prefix_java_common}osgi(org.apache.httpcomponents.httpmime) >= %{hc_client_bundle_version}

# The version of asm that this package builds against gets bundled in
# See https://fedorahosted.org/fpc/ticket/226 for the same issue in another package
Provides: %{?scl_prefix}bundled(%{?scl_prefix_maven}mvn(%{object_web_asm_maven_coords})

%description
Thermostat is a monitoring and instrumentation tool for the Hotspot JVM,
with support for monitoring multiple JVM instances. The system is made
up of two processes: an Agent, which collects data, and a Client which
allows users to visualize this data. These components communicate via
a MongoDB-based storage layer. A pluggable agent and gui framework
allows for collection and visualization of performance data beyond that
which is included out of the box.

%package javadoc
Summary:    Javadocs for %{pkg_name}
Group:      Documentation
%{!?scl:
Requires:   javapackages-tools
}

BuildArch:  noarch

%description javadoc
This package contains the API documentation for %{pkg_name}

%package webapp
Summary:    Web storage endpoint for Thermostat
BuildArch:  noarch
%if 0%{?is_rhel_6}
Requires:   %{tomcat_name}
%else
Requires:   %{tomcat_name} >= 7.0.54
%endif
Requires:   %{name} = %{version}-%{release}
Requires:   %{?scl_prefix_java_common}apache-commons-fileupload

%description webapp
This package contains the exploded web archive. This web application
contains the server-side parts for deploying thermostat with improved
security.

%prep
%{?scl:scl enable %{scl_maven} %{scl_java_common} %{scl_mongodb} %{scl} - << "EOF"}
# When Source0 is released version. 
%setup -q -n %{pkg_name}-%{version}
# When Source0 is a snapshot from HEAD.
#%%setup -q -n %%{pkg_name}-%%{hgrev}
# When Source 0 is a snapshot from a release branch.
#%%setup -q -n %%{pkg_name}-%%{major}-%%{minor}-%%{hgrev}
%patch1 -p1
%patch2 -p1

# Replace thermostatrc with Fedora's version
cp %{SOURCE4} distribution/config/thermostatrc

# Fix up artifact names which have different name upstream
#  lucene
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene" vm-heap-analysis/common
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene" vm-heap-analysis/distribution
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene-analyzers-common" vm-heap-analysis/common
%pom_remove_dep "org.apache.servicemix.bundles:org.apache.servicemix.bundles.lucene-analyzers-common" vm-heap-analysis/distribution
%pom_add_dep "org.apache.lucene:lucene-analyzers:%{lucene_version}" vm-heap-analysis/common
%pom_add_dep "org.apache.lucene:lucene-analyzers:%{lucene_version}" vm-heap-analysis/distribution
%pom_add_dep "org.apache.lucene:lucene-core:%{lucene_version}" vm-heap-analysis/common
%pom_add_dep "org.apache.lucene:lucene-core:%{lucene_version}" vm-heap-analysis/distribution
# Fix up artifact names for jgraphx
%pom_remove_dep "org.tinyjee.jgraphx:jgraphx"
%pom_add_dep "com.mxgraph:jgraphx:%{jgraphx_bundle_version}.0"
%pom_remove_dep "org.tinyjee.jgraphx:jgraphx" thread/client-swing
%pom_add_dep "com.mxgraph:jgraphx:%{jgraphx_bundle_version}.0" thread/client-swing
#  httpclient
%pom_remove_dep org.apache.httpcomponents:httpclient-osgi web/client
%pom_add_dep org.apache.httpcomponents:httpclient:4.4.0 web/client
%pom_remove_dep org.apache.httpcomponents:httpclient-osgi client/command
%pom_add_dep org.apache.httpcomponents:httpclient:4.4.0 client/command
#  add httpmime dep. this is included in upstreams' strange jar
%pom_add_dep org.apache.httpcomponents:httpmime:4.4.0 web/client
#  httpcore
%pom_remove_dep org.apache.httpcomponents:httpcore-osgi web/client
%pom_add_dep org.apache.httpcomponents:httpcore:4.4.0 web/client
# need jline 2.13 (otherwise this resolves to jline 1)
%pom_xpath_remove "pom:properties/pom:jline.version"
%pom_xpath_inject "pom:properties" "<jline.version>2.13</jline.version>"
#  netty
#%%pom_remove_dep org.jboss.netty:netty 
%pom_remove_dep org.jboss.netty:netty common/command
%pom_remove_dep org.jboss.netty:netty client/command
%pom_remove_dep org.jboss.netty:netty agent/command
%pom_add_dep io.netty:netty:%{netty_bundle_version} common/command
%pom_add_dep io.netty:netty:%{netty_bundle_version} client/command
%pom_add_dep io.netty:netty:%{netty_bundle_version} agent/command

# Don't use maven-exec-plugin. We do things manually in order to avoid this
# additional dep. It's used in agent/core/pom.xml et.al.
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin agent/core
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin keyring
%pom_remove_plugin org.codehaus.mojo:exec-maven-plugin laf-utils

# Remove license plugin in main pom.xml
%pom_remove_plugin com.mycila:license-maven-plugin

# Remove javacoco-coverage plugin (in main pom.xml and web/war/pom.xml)
%pom_remove_plugin org.jacoco:jacoco-maven-plugin
%pom_remove_plugin org.jacoco:jacoco-maven-plugin web/war

# Remove pmd plugin
%pom_remove_plugin org.apache.maven.plugins:maven-pmd-plugin

# Remove m2e's lifecyle plugin
%pom_remove_plugin org.eclipse.m2e:lifecycle-mapping

# Disable test modules
%pom_disable_module test common
%pom_disable_module integration-tests
%pom_disable_module testutils storage
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils vm-cpu/common
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils vm-profiler/common
%pom_remove_dep com.redhat.thermostat:thermostat-storage-testutils thread/collector
# Disable some dev modules we don't ship
%pom_disable_module ide-launcher dev
%pom_disable_module schema-info-command dev
%pom_disable_module perflog-analyzer dev
# SCL would need maven archetype packaging plugin for this to work. For now package in
# Fedora only.
%{?scl:
%pom_disable_module archetype-ext dev
%pom_disable_module multi-module-plugin-archetype dev
}
%pom_remove_dep com.redhat.thermostat:thermostat-schema-info-distribution distribution

# Remove system scope and systempath from tools jar dependency.
%pom_xpath_remove -r "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:scope"
%pom_xpath_remove -r "pom:dependencies/pom:dependency[pom:groupId='com.sun']/pom:systemPath"

# Remove depencency on the web archive for web-storage-service we'll make deps
# available manually
%pom_remove_dep "com.redhat.thermostat:thermostat-web-war" web/endpoint-plugin/web-service

# jetty-schemas is not available in SCLs
%{?scl:
%pom_remove_dep org.eclipse.jetty.toolchain:jetty-schemas web/endpoint-plugin/distribution
}
# Skip automatic installation of zip artifacts. We only use it for our build
# to assemble plug-ins.
%mvn_package com.redhat.thermostat::zip: __noinstall
# Skip automatic installation of the war module.
# We install it manually. Without this "config" %mvn_build -f
# fails. See RHBZ#963838
%mvn_package com.redhat.thermostat:thermostat-web-war __noinstall
# Don't install :thermostat-common-test, it's a test only dep which
# isn't run during the build.
%mvn_package com.redhat.thermostat:thermostat-common-test __noinstall

# These are just upstream build helpers. Don't install them.
%mvn_package com.redhat.thermostat:thermostat-distribution __noinstall
%mvn_package com.redhat.thermostat:thermostat-assembly __noinstall

# thermostat-web-server and thermostat-web-endpoint should be part of
# the webapp sub-package
%mvn_package com.redhat.thermostat:thermostat-web-server webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint-plugin" webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint:pom:" webapp
%mvn_package "com.redhat.thermostat:thermostat-web-endpoint-distribution:pom:" webapp
# Do not embed jgraphx dependency in thread client.
%pom_xpath_remove "pom:project/pom:build/pom:plugins/pom:plugin[pom:artifactId='maven-bundle-plugin']/pom:configuration/pom:instructions/pom:Embed-Dependency" thread/client-swing
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl_java_common} %{scl_mongodb} %{scl} - << "EOF"}
export CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS"
# Set JAVA_HOME. make uses this
. /usr/share/java-utils/java-functions
set_jvm
export JAVA_HOME

################## Build JNI bits ########################
# JNI bits depend on NativeLibraryResolver so compile that
# first and relevant Java classes with native methods
# after.
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
  autoreconf --install
  ./configure
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

# This is roughly equivalent to:
#   mvn 
#     -Dthermostat.home=... \
#    install javadoc:aggregate
# Everything after '--' is passed to plain xmvn/mvn
%mvn_build -f -- -Dthermostat.home=%{thermostat_home} \
                 -Dthermostat.jdk.home=%{jdk_base} \
                 -Dthermostat.system.user=thermostat \
                 -Dthermostat.system.group=thermostat \
                 -Dthermostat.desktop.app.name=%{thermostat_desktop_app_name} \
                 -Dnetty.version=%{netty_bundle_version}.Final \
                 -Dtomcat=%{tomcat_version} \
                 -Dpkg_name=%{pkg_name} \
                 -Dcommons-logging.version=%{logging_bundle_version} \
                 -Dcommons-collections.version=%{collections_bundle_version} \
                 -Dcommons-codec.osgi-version=%{codec_bundle_version} \
                 -Dcommons-beanutils.version=%{beanutils_bundle_version} \
                 -Dgson.version=%{gson_bundle_version} \
                 -Dmongo-driver.osgi-version=%{mongo_bundle_version} \
                 -Dhttpcomponents.core.version=%{hc_core_bundle_version} \
                 -Dhttpcomponents.client.version=%{hc_client_bundle_version} \
                 -Dhttpcomponents.mime.version=%{hc_client_bundle_version} \
                 -Djansi.version=%{jansi_version} \
                 -Djcommon.osgi.version=%{jcommon_bundle_version} \
                 -Djfreechart.osgi.version=%{jfreechart_bundle_version} \
                 -Dlucene-core.bundle.symbolic-name=org.apache.lucene.core \
                 -Dlucene-analysis.bundle.symbolic-name=%{lucene_analysis_core_bsn} \
                 -Dlucene.osgi-version=%{lucene_version} \
                 -Dosgi.compendium.bundle.symbolic-name=org.osgi.compendium \
                 -Dosgi.compendium.osgi-version=4.1.0 \
                 -Djgraphx.osgi.version=%{jgraphx_bundle_version}.0 \
                 -Djetty.javax.servlet.osgi.version=%{javax_servlet_bundle_version} \
                 -Djavax.servlet.bsn=%{javax_servlet_bsn} \
                 -Djetty.version=%{jetty_version}
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl_java_common} %{scl_mongodb} %{scl} - << "EOF"}
#######################################################
# Thermostat core
#######################################################
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/%{pkg_name}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{system_confdir}/sysconfig
# JNI things live there
mkdir -p %{buildroot}%{_libdir}/%{pkg_name}
mkdir -p %{buildroot}%{_jnidir}
# Systemd/initrd files live there
%if 0%{?is_rhel_6}
mkdir -p %{buildroot}%{system_initrddir}
%else
mkdir -p %{buildroot}%{_unitdir}
%endif
# Thermostat icon lives there
mkdir -p %{buildroot}%{system_root_datadir}/icons/hicolor/scalable/apps
# Thermostat desktop lives there
mkdir -p %{buildroot}%{system_root_datadir}/applications
# Thermostat app data file lives there
mkdir -p %{buildroot}%{system_root_datadir}/appdata
# Example config files are in docdir
mkdir -p %{buildroot}%{_docdir}/%{pkg_name}
# Man page
mkdir -p %{buildroot}%{_mandir}/man1

# Dance the xmvn install limbo. This only makes sense if %mvn_build does NOT
# have the '-i' switch.
%mvn_install

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

# Install systemd unit/init script files for storage
%if 0%{?is_rhel_6}
  # FIXME: No way to run thermostat storage via init.d script.
%else
  pushd distribution/target/packaging/systemd
    sed -i 's/User=thermostat/User=root/g' thermostat-agent.service
    sed -i 's/Group=thermostat/Group=root/g' thermostat-agent.service
    # FIXME: install or not-to-install agent service running as root?
    #        Currently: Don't install.
    %{?scl:
    sed -i 's#ExecStart=.*#ExecStart=/usr/bin/scl enable $RH_THERMOSTAT16_SCLS_ENABLED -- %{thermostat_home}/bin/thermostat storage --start#g' thermostat-storage.service
    sed -i 's#ExecStop=.*#ExecStop=/usr/bin/scl enable $RH_THERMOSTAT16_SCLS_ENABLED -- %{thermostat_home}/bin/thermostat storage --stop#g' thermostat-storage.service
    sed -i 's#EnvironmentFile=.*#EnvironmentFile=%{_sysconfdir}/sysconfig/%{name}#g' thermostat-storage.service
    }
    cp -a thermostat-storage.service %{buildroot}%{_unitdir}/%{?scl_prefix}%{pkg_name}-storage.service
  popd
%endif

# Install tmpfiles.d config file for /var/run/%{pkg_name}
mkdir -p %{buildroot}%{system_tmpfilesdir}
# Maintain rh-thermostat16-thermostat instead of thermostat
pushd distribution/target/packaging/systemd/tmpfiles.d

sed -i 's#/var/run/thermostat#/var/run/rh-thermostat16-thermostat#g' %{pkg_name}.conf
install -m 0644 %{pkg_name}.conf %{buildroot}%{system_tmpfilesdir}/%{name}.conf

popd

# Install thermostat man page
install -m 0644 distribution/packaging/shared/man/%{pkg_name}.1 %{buildroot}%{_mandir}/man1/%{pkg_name}.1

# Install bash completions. Note those won't work on EL 6 unless somebody
# finds a bash-completion package somewhere (e.g. via EPEL)
# FIXME: Install it outside the SCL
# (i.e. /usr/share directly) since there does not seem to be support
# for it otherwise.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1264094
mkdir -p %{buildroot}%{system_root_datadir}/bash-completion/completions
install -pm 644 distribution/target/packaging/bash-completion/thermostat-completion %{buildroot}%{system_root_datadir}/bash-completion/completions/%{name}

# install files needed for proper desktop integration
install -m 0644 distribution/target/packaging/desktop/%{pkg_name}.desktop %{buildroot}%{system_root_datadir}/applications/%{name}.desktop
install -m 0644 distribution/target/packaging/icons/256px.svg %{buildroot}%{system_root_datadir}/icons/hicolor/scalable/apps/%{name}.svg
install -m 0644 distribution/target/packaging/desktop/%{pkg_name}.appdata.xml %{buildroot}%{system_root_datadir}/appdata/%{name}.appdata.xml

rm -rf distribution/target/image/bin/%{pkg_name}.orig
# Remove developer setup things.
rm distribution/target/image/bin/thermostat-devsetup
rm distribution/target/image/etc/devsetup.input

# We'll install webapp later, move it out of the way
mv distribution/target/image/webapp webstorage-webapp
# Move everything else into $THERMOSTAT_HOME
cp -a distribution/target/image %{buildroot}%{thermostat_home}

# Replace jars with symlinks to installed libs
pushd %{buildroot}%{thermostat_home}/libs
  xmvn-subst %{xmvn_subst_args}
popd
# Do the same for thermostat plugin dirs
pushd %{buildroot}%{thermostat_home}/plugins
for plugin_name in $(ls); do
  pushd $plugin_name
    xmvn-subst %{xmvn_subst_args}
  popd
done
popd
# Remove duplicate tools*.jar files which makes the resulting
# RPM insanely large (21 * 20 MB) ~= 410 MB => ~90 to 100 MB compressed
find %{buildroot}%{thermostat_home} -name 'tools*.jar' | xargs rm
# Remove jzlib.jar/jzlib-any.jar which maven thinks we need but we don't
# actually need.
rm -rf %{buildroot}%{thermostat_home}/libs/jzlib*.jar

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

# Symlink the thermostat script(s) in /usr/bin
ln -s %{_datarootdir}/%{pkg_name}/bin/thermostat \
    %{buildroot}%{_bindir}/thermostat
ln -s %{_datarootdir}/%{pkg_name}/bin/thermostat-setup \
    %{buildroot}%{_bindir}/thermostat-setup
ln -s %{_datarootdir}/%{pkg_name}/bin/thermostat-common \
    %{buildroot}%{_bindir}/thermostat-common

# Move config files to /etc and symlink stuff under
# $THERMOSTAT_HOME/etc to it. Put example configs
# in docdir.
mv %{buildroot}%{thermostat_home}/etc/examples \
   %{buildroot}%{_docdir}/%{pkg_name}/
mv %{buildroot}%{thermostat_home}/etc/* \
   %{buildroot}%{_sysconfdir}/%{pkg_name}
rmdir %{buildroot}%{thermostat_home}/etc
ln -s %{_sysconfdir}/%{pkg_name}/ \
          %{buildroot}%{thermostat_home}/etc

# Install sysconfig file. This is so as to set various env vars
# which controls how thermostat behaves. In the systemd case we
# want thermostat to run as system user.
sed 's#__thermostat_home__#%{thermostat_home}/#g' %{SOURCE1} > thermostat_sysconfig.env
sed -i 's#__thermostat_user_home__#%{user_thermostat_home}/#g' thermostat_sysconfig.env
cp thermostat_sysconfig.env %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# Set up directory structure for running thermostat storage/
# thermostat agend via systemd
%{__install} -d -m 0775 %{buildroot}%{system_datadir}
# Create a setup-complete.stamp file so as to prevent the launcher hook from
# successfully running the thermostat1-thermostat-storage service.
echo "setup-complete.stamp for thermostat-storage systemd service" > %{buildroot}%{system_datadir}/setup-complete.stamp
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

# Symlink system user folders as well for storage as a systemd service
%{?scl:
  %{__install} -d -m 0775 %{buildroot}%{user_datadir}
  %{__install} -d -m 0775 %{buildroot}%{user_statedir}
  %{__install} -d -m 0775 %{buildroot}%{user_logdir}
  %{__install} -d -m 0775 %{buildroot}%{user_cachedir}

  ln -s %{system_datadir} %{buildroot}%{user_datadir}/%{pkg_name}
  ln -s %{system_statedir} %{buildroot}%{user_statedir}/%{pkg_name}
  ln -s %{system_logdir} %{buildroot}%{user_logdir}/%{pkg_name}
  ln -s %{system_cachedir} %{buildroot}%{user_cachedir}/%{pkg_name}
}
#######################################################
# Thermostat web storage webapp
#######################################################
mkdir -p %{buildroot}%{thermostat_catalina_base}/webapps
pushd webstorage-webapp
# Fixup THERMOSTAT_HOME in web.xml
 sed -i '/<param-name>THERMOSTAT_HOME<[/]param-name>/,/<param-value>.*<[/]param-value>/{ s$<param-value>.*</param-value>$<param-value>%{thermostat_home}</param-value>$ }' \
 WEB-INF/web.xml
popd
cp -r webstorage-webapp %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}
# Provide a link to webapp in THERMOSTAT_HOME
ln -s %{thermostat_catalina_base}/webapps/%{pkg_name} %{buildroot}%{thermostat_home}/webapp
 
# Replace jars with symlinks
pushd %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib
  xmvn-subst %{xmvn_subst_args}
popd

# Remove tools.jar (coming from the JVM). We also don't need jzlib.jars.
# The latter jar might be a (broken?) symlink which makes web-storage-service fail.
rm -rf %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib/jzlib*.jar
rm -rf %{buildroot}%{thermostat_catalina_base}/webapps/%{pkg_name}/WEB-INF/lib/tools*.jar

# We use a custom CATALINA_BASE with core tomcat directories
# symlinked. This allows us to deploy the thermostat webapp
# nicely configured without any configuration required prior
# starting tomcat via systemd.
sed 's#__catalina_base__#%{thermostat_catalina_base}#g' %{SOURCE3} > tomcat_service_thermostat.txt
sed -i 's#__catalina_home__#%{system_catalina_home}#g' tomcat_service_thermostat.txt
sed -i 's#__jaas_config__#%{_sysconfdir}/%{pkg_name}/%{pkg_name}_jaas.conf#g' tomcat_service_thermostat.txt
%{?scl:
  # install the init script on RHEL 6
  %if 0%{?is_rhel_6}
    sed 's#__service_name__#%{thermostat_tomcat_service_name}#g' %{SOURCE5} > tomcat_initd.sh
    cp tomcat_initd.sh %{buildroot}%{system_initrddir}/%{thermostat_tomcat_service_name}
    cp tomcat_service_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
  %else
    # RHEL 7

cat <<SYSTEMD_TOMCAT_ENV >systemd_tomcat_env_thermostat.txt
# This file is sourced via the thermostat tomcat systemd service.
SERVICE_NAME=%{thermostat_tomcat_service_name}
SYSTEMD_TOMCAT_ENV

    cp systemd_tomcat_env_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
    # Install file twice, since RHEL 7.0 and RHEL 7.1 have different tomcat versions.
    # The first file is used by thermostat1-thermostat-tomcat's service. The second one is
    # used by "tomcat@thermostat".
    cp tomcat_service_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
    # systemd converts - in names to / in file paths:
    mkdir -p %{buildroot}%{system_confdir}/sysconfig/tomcat@rh
    cp tomcat_service_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/tomcat@rh/thermostat16 
    sed "s#__service_file_name__#%{thermostat_tomcat_service_name}#g" %{SOURCE6} > systemd_tomcat_thermostat.service
    sed -i "s#__service_file_path__#%{system_confdir}/sysconfig#g" systemd_tomcat_thermostat.service
    cp systemd_tomcat_thermostat.service %{buildroot}%{_unitdir}/%{thermostat_tomcat_service_name}.service
  %endif
}
%{!?scl:
  cp tomcat_service_thermostat.txt %{buildroot}%{system_confdir}/sysconfig/tomcat@%{pkg_name}
}
# Create a symlinked CATALINA_BASE in order to make tomcat deploy
# the scl-ized tomcat web-app. We use our own copy of conf/server.xml in order
# to not port-conflict with system tomcat. See RHBZ#1054396
pushd %{buildroot}/%{thermostat_catalina_base}
  for i in lib logs work temp; do
    ln -s %{system_catalina_home}/$i $i
  done
  mkdir conf
popd
# Symlink everything other than server.xml
pushd %{system_catalina_home}/conf
  for i in *; do
    ln -s %{system_catalina_home}/conf/$i %{buildroot}/%{thermostat_catalina_base}/conf/$i
  done
  rm %{buildroot}/%{thermostat_catalina_base}/conf/server.xml
  cp -p server.xml %{buildroot}/%{thermostat_catalina_base}/conf/server.xml
popd
pushd %{buildroot}/%{thermostat_catalina_base}/conf
  # Fix the connector port, use a different access log file name
  sed -i -e 's/<Connector port="8080"/<Connector port="%{thermostat_catalina_port}"/g' \
         -e 's/prefix="localhost_access_log."/prefix="localhost_thermostat_access_log."/g' server.xml
popd
%{?scl:
# Make tomcat with custom catalina base happy (not complain about this dir missing)
mkdir -p %{buildroot}/%{_root_localstatedir}/log/%{thermostat_tomcat_service_name}
}
%{?scl:EOF}

%check
# Perform a sanity check so as to ensure that JAVA_HOME will point to a
# stable path (across OpenJDK package updates).
JDK_HOME_CANDIDATE=$(grep 'jdk_home_candidate=' %{buildroot}/%{thermostat_home}/bin/thermostat-common | cut -d= -f2 | cut -d\" -f2)
test "${JDK_HOME_CANDIDATE}" = "%{jdk_base}"

%pre
%{?scl:
  __bin_dir=%{system_sbindir}
}
%{!?scl:
  __bin_dir=%{_sbindir}
}
# add the thermostat user and group
${__bin_dir}/groupadd -r thermostat 2>/dev/null || :
${__bin_dir}/useradd -c "Thermostat system user" -g thermostat \
    -s /sbin/nologin -r -d %{thermostat_home} thermostat 2>/dev/null || :

%post
# Install but don't activate

%if 0%{?with_systemd}
%systemd_post %{?scl_prefix}%{pkg_name}-storage.service
%endif
# Required for icon cache (i.e. Thermostat icon)
/bin/touch --no-create %{system_root_datadir}/icons/hicolor &>/dev/null || :

%post webapp
# install but don't activate
%if 0%{?is_rhel_6}
  /sbin/chkconfig --add %{thermostat_tomcat_service_name}
%endif

%preun
%if 0%{?with_systemd}
%systemd_preun %{?scl_prefix}%{pkg_name}-storage.service
%endif

%postun
# Required for icon cache (i.e. Thermostat icon)
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{system_root_datadir}/icons/hicolor &> /dev/null
    /usr/bin/gtk-update-icon-cache %{system_root_datadir}/icons/hicolor &>/dev/null || :
fi
%if 0%{?with_systemd}
%systemd_postun %{?scl_prefix}%{pkg_name}-storage.service
%endif

%posttrans
# Required for icon cache (i.e. Thermostat icon)
/usr/bin/gtk-update-icon-cache %{system_root_datadir}/icons/hicolor &>/dev/null || :

%files -f .mfiles
%doc LICENSE
# %license macro not available in RHEL 6
%if 0%{?is_rhel_6}
%doc COPYING
%doc OFL.txt
%else
%license COPYING
%license OFL.txt
%endif
%doc README
%doc README.api
# Own appropriate files in /etc/ part of them belong to the
# webapp sub-package
%config(noreplace) %dir %{_sysconfdir}/%{pkg_name}
# This file is only used by the systemd service running agent.
# Only root should be able to read/write to it.
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/%{pkg_name}/agent.auth
%config(noreplace) %{_sysconfdir}/%{pkg_name}/agent.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/db.properties
%config(noreplace) %{_sysconfdir}/%{pkg_name}/logging.properties
%config %{_sysconfdir}/%{pkg_name}/bash-complete-logging.properties
%{system_root_datadir}/bash-completion/completions/%{name}
# Own containing directories since bash-completion package might not
# be installed
%dir %{system_root_datadir}/bash-completion/completions
%dir %{system_root_datadir}/bash-completion
# Own desktop related files
%{system_root_datadir}/applications/%{name}.desktop
%{system_root_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{system_root_datadir}/appdata/%{name}.appdata.xml
%config(noreplace) %{_sysconfdir}/%{pkg_name}/plugins.d
%config(noreplace) %{_sysconfdir}/%{pkg_name}/ssl.properties
%config %{_sysconfdir}/%{pkg_name}/commands
%config %{_sysconfdir}/%{pkg_name}/osgi-export.properties
%config %{_sysconfdir}/%{pkg_name}/thermostatrc
# Required for systemd services
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_datadir}/%{pkg_name}/etc
%{_datadir}/%{pkg_name}/bin
# Command channel script should be owned by thermostat user to drop root privileges
%attr(0755,thermostat,thermostat) %{_datadir}/%{pkg_name}/bin/thermostat-command-channel
%{_datadir}/%{pkg_name}/libs
%{_datadir}/%{pkg_name}/plugins/local
%{_datadir}/%{pkg_name}/plugins/host-cpu
%{_datadir}/%{pkg_name}/plugins/host-memory
%{_datadir}/%{pkg_name}/plugins/host-overview
%{_datadir}/%{pkg_name}/plugins/killvm
%{_datadir}/%{pkg_name}/plugins/notes
%{_datadir}/%{pkg_name}/plugins/numa
%{_datadir}/%{pkg_name}/plugins/storage-profile
%{_datadir}/%{pkg_name}/plugins/thread
%{_datadir}/%{pkg_name}/plugins/validate
%{_datadir}/%{pkg_name}/plugins/setup
%{_datadir}/%{pkg_name}/plugins/vm-classstat
%{_datadir}/%{pkg_name}/plugins/vm-compiler
%{_datadir}/%{pkg_name}/plugins/vm-cpu
%{_datadir}/%{pkg_name}/plugins/vm-gc
%{_datadir}/%{pkg_name}/plugins/vm-heap-analysis
%{_datadir}/%{pkg_name}/plugins/vm-io
%{_datadir}/%{pkg_name}/plugins/vm-jmx
%{_datadir}/%{pkg_name}/plugins/vm-memory
%{_datadir}/%{pkg_name}/plugins/vm-numa
%{_datadir}/%{pkg_name}/plugins/vm-overview
%{_datadir}/%{pkg_name}/plugins/vm-profiler
%{_datadir}/%{pkg_name}/plugins/vm-find
%{_datadir}/%{pkg_name}/plugins/experimental
%dir %{_datadir}/%{pkg_name}/plugins
%dir %{_datadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_javadir}/%{pkg_name}
%{_datadir}/%{pkg_name}/cache
%{_datadir}/%{pkg_name}/data
%{_datadir}/%{pkg_name}/logs
%{_datadir}/%{pkg_name}/run
%{_libdir}/%{pkg_name}
%dir %{_jnidir}/%{pkg_name}
%{_jnidir}/thermostat-*.jar
%{_bindir}/thermostat
%{_bindir}/thermostat-setup
%{_bindir}/thermostat-common
%{_mandir}/man1/%{pkg_name}.1*
%if 0%{?with_systemd}
%{_unitdir}/%{?scl_prefix}%{pkg_name}-storage.service
%endif
%{system_tmpfilesdir}/%{name}.conf
# To these directories get written to when thermostat storage/agent
# run as systemd services
%{?scl:
  %{user_datadir}/%{pkg_name}
  %{user_statedir}/%{pkg_name}
  %{user_logdir}/%{pkg_name}
  %{user_cachedir}/%{pkg_name}
}

%attr(0770,thermostat,thermostat) %dir %{system_datadir}
%attr(0660,thermostat,thermostat) %{system_datadir}/setup-complete.stamp
%attr(0770,thermostat,thermostat) %dir %{system_cachedir}
%attr(0770,thermostat,thermostat) %dir %{system_logdir}
%attr(0770,thermostat,thermostat) %dir %{system_statedir}
%doc %{_docdir}/%{pkg_name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE
# license macro not available in RHEL 6
%if 0%{?is_rhel_6}
%doc COPYING
%doc OFL.txt
%else
%license COPYING
%license OFL.txt
%endif
%{?scl:
  %{_datarootdir}/javadoc/%{pkg_name}
}

%files webapp -f .mfiles-webapp
%{thermostat_catalina_base}
%config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}_jaas.conf
%config(noreplace) %{_sysconfdir}/%{pkg_name}/web-storage-service.properties
# Those files should be readable by root and tomcat only
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}-users.properties
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/%{pkg_name}-roles.properties
%attr(0640,root,tomcat) %config(noreplace) %{_sysconfdir}/%{pkg_name}/web.auth
# We need an extra file in order to make thermostat-webapp work with
# our custom CATALINA_BASE. This sets the JAAS-config option.
%{?scl:
%if 0%{?is_rhel_6}
  %config(noreplace) %{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
  # thermostat tomcat init script
  %attr(0755,root,root) %{system_initrddir}/%{thermostat_tomcat_service_name}
  %attr(0770,tomcat,tomcat) %dir %{_root_localstatedir}/log/%{thermostat_tomcat_service_name}
%else
  %config(noreplace) %{system_confdir}/sysconfig/%{thermostat_tomcat_service_name}
  %{_unitdir}/%{?scl_prefix}%{pkg_name}-tomcat.service
  %attr(0770,tomcat,tomcat) %dir %{_root_localstatedir}/log/%{thermostat_tomcat_service_name}
  # File used by RHEL-7.1's tomcat@thermostat service.
  # escaped form of %%{scl_name}
  %dir %{system_confdir}/sysconfig/tomcat@rh
  %config(noreplace) %{system_confdir}/sysconfig/tomcat@rh/thermostat16
%endif
}
%{!?scl:
  %config(noreplace) %{system_confdir}/sysconfig/tomcat@%{pkg_name}
}
%{_datadir}/%{pkg_name}/webapp
%{_datadir}/%{pkg_name}/plugins/embedded-web-endpoint

%changelog
* Wed Jan 18 2017 Jie Kang <jkang@redhat.com> - 1.6.6-3
- Add self-br for proper symlinking

* Wed Jan 18 2017 Jie Kang <jkang@redhat.com> - 1.6.6-2
- Fix jdk requires for el6 case with conditional

* Tue Jan 17 2017 Jie Kang <jkang@redhat.com> - 1.6.6-1
- Rebase to latest Thermostat 1.6.6. Resolves rhbz#1398394
- Use jline from rh-java-common instead of rh-thermostat16
- Remove self-br for bootstrap build
- Use java-devel-openjdk requires instead of a hard
  require on java-1.7.0-openjdk. Resolves rhbz#1398232

* Fri Jan 13 2017 Jie Kang <jkang@redhat.com> - 1.6.4-7
- Use /usr/lib/jvm/java for jdk base, a link managed by
  alternatives. Resolves rhbz#1398252

* Wed Jan 11 2017 Jie Kang <jkang@redhat.com> - 1.6.4-6
- Update version of gson package

* Wed Oct 26 2016 Jie Kang <jkang@redhat.com> - 1.6.4-5
- Add patch for fixing verified token removal
  Resolves RHBZ#1388898

* Wed Oct 12 2016 Jie Kang <jkang@redhat.com> - 1.6.4-4
- Add patch for fixing storage initilization on
  concurrent connections. Resolves RHBZ#1329003

* Tue Oct 11 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.6.4-3
- Change owner of thermostat-command-channel script to
  thermostat:thermostat. Resolves: RHBZ#1379702

* Thu Sep 15 2016 Jie Kang <jkang@redhat.com> - 1.6.4-2
- Add self-br for proper symlinking

* Thu Sep 15 2016 Jie Kang <jkang@redhat.com> - 1.6.4-1
- Update to upstream 1.6.4 release
- Resolves RHBZ#1364549

* Wed Sep 14 2016 Jie Kang <jkang@redhat.com> - 1.6.2-2
- Add self-br for proper symlinking

* Wed Sep 14 2016 Jie Kang <jkang@redhat.com> - 1.6.2-1
- Update to upstream 1.6.2 release
- Resolves RHBZ#1364549

* Thu Sep 01 2016 Jie Kang <jkang@redhat.com> - 1.6.0-11
- Own in collection directories
- Resolves RHBZ#1371518

* Thu Sep 01 2016 Jie Kang <jkang@redhat.com> - 1.6.0-10
- Fix broken symlinks to tomcat files for el6
- Resolves RHBZ#1371497, RHBZ#1371691

* Fri Aug 05 2016 Jie Kang <jkang@redhat.com> - 1.6.0-9
- Fix systemd install/uninstall for el6 where
  rh-thermostat16-thermostat-storage.service is not available

* Wed Aug 03 2016 Jie Kang <jkang@redhat.com> - 1.6.0-8
- Add self-br for proper symlinking

* Wed Aug 03 2016 Jie Kang <jkang@redhat.com> - 1.6.0-7
- Remove self-br for bootstrap build

* Wed Aug 03 2016 Jie Kang <jkang@redhat.com> - 1.6.0-6
- Merge changes from branch rhscl-2.3-rh-thermosta16-rhel-7 from 1.6.0-7
- Fix rh-thermostat16-thermostat-storage.service
- Prevent /var/run/rh-thermostat16-thermostat file from 
  disappearing after system reboot

* Tue Jul 26 2016 Jie Kang <jkang@redhat.com> - 1.6.0-5
- Merge changes from branch rhscl-2.3-rh-thermostat16-rhel-7 from 1.6.0-3 to 1.6.0-6
- Use /dev/urandom for tomcat@thermostat service.
- Resolves: RHBZ#1328972
- Use java-common package for apache-commons-fileupload
- Fix typo in thermostatrc script replacement
- Make rh-thermostat16-thermostat parallel-installable with thermostat1-thermostat

* Thu Jul 21 2016 Jie Kang <jkang@redhat.com> - 1.6.0-4
- Add self-br for proper symlinking

* Thu Jul 21 2016 Jie Kang <jkang@redhat.com> - 1.6.0-3
- Remove self-br for initial build

* Thu Jul 14 2016 Jie Kang <jkang@redhat.com> - 1.6.0-2
- Add self-br for proper symlinking

* Thu Jul 14 2016 Jie Kang <jkang@redhat.com> - 1.6.0-1
- Update to upstream 1.6.0 release.

* Mon Jun 27 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.5.9-5
- Fix lucene analyzers core bundle symbolic name.

* Mon Jun 27 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.5.9-4
- Fix bundle loading errors for "thermostat local".

* Mon Jun 27 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.5.9-3
- Fix bundle loading errors on framework boot.

* Fri Jun 24 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.5.9-2
- Add self-br for proper symlinking.

* Fri Jun 24 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.5.9-1
- Initial package.
