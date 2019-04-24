from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class SnmpConan(ConanFile):
    name = "net-snmp"
    version = "5.8"
    license = "http://net-snmp.sourceforge.net/about/license.html"
    url = "https://sourceforge.net/projects/net-snmp/files/net-snmp/5.8/net-snmp-5.8.tar.gz"
    author = "Amina Ramazanova / InSAT"
    description = "net-snmp package"
    topics = ("net-snmp", "snmp")
    scm = {
         "type": "git",
         "subfolder": "net-snmp",
         "url": "http://dev.arenoros.info/MS4/Library/_git/net-snmp",
         "revision": "net-snmp-with-openssl"
    }
    settings = "os", "arch", "compiler", "arch_build"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    requires = "OpenSSL/1.1.1@conan/stable"
    source_folder = "net-snmp"

    def configure(self):
        self.options["OpenSSL"].shared = True

    def system_requirements(self):
        self.global_system_requirements=True

    def source(self):
        if self.settings.os == "Windows":
            tools.patch(patch_file="net-snmp\\net-snmp.patch", base_path=os.path.join(os.getcwd(), "net-snmp"))

    def linux_build(self):
        env_build = AutoToolsBuildEnvironment(self)
        with tools.chdir(os.path.join(self.source_folder, "net-snmp")):
            configure = "./configure --with-default-snmp-version=3 \
            --with-sys-contact=@@no.where --with-sys-location=Unknown \
            --with-logfile=/var/log/snmpd.log \
            --with-persistent-directory=/var/net-snmp \
            --disable-manuals \
            --disable-embedded-perl \
            --disable-perl-cc-checks\
            --with-openssl=%s \
            --prefix=%s" % (self.deps_cpp_info["OpenSSL"].rootpath, os.getcwd())
            #env_build.configure(args=[configure], build=False, host=False, use_default_install_dirs=False)
            self.run(configure)
            env_build.make()
            env_build.install()


    def windows_build(self):
        os.environ['OPENSSL_INCLUDE_PATH'] = self.deps_cpp_info["OpenSSL"].include_paths[0]
        os.environ['OPENSSL_LIB_PATH'] = self.deps_cpp_info["OpenSSL"].lib_paths[0]
        config_command = "perl build.pl"
        self.output.warn(config_command)
        with tools.chdir(os.path.join(self.source_folder, "net-snmp\\win32")):
            self.run(config_command)
        self.output.writeln(" ")

    def build(self):
        if self.settings.os == "Windows":
            self.windows_build()
        elif self.settings.os == "Linux":
            self.linux_build()
        else:
            raise Exception("Unsupported operating system: %s" % self.settings.os)


    def package(self):
        self.copy("*.h", dst="include", src="net-snmp")
        if self.settings.os == "Windows":
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
        else:
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = ["netsnmp", "netsnmpagent", "netsnmpmibs", "netsnmptrapd"]
