from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class SnmpConan(ConanFile):
    name = "net-snmp"
    version = "5.8"
    license = "http://net-snmp.sourceforge.net/about/license.html"
    url = "https://sourceforge.net/projects/net-snmp/files/net-snmp/5.8/net-snmp-5.8.tar.gz"
    author = "InSAT"
    description = "net-snmp package"
    topics = ("net-snmp", "snmp")
    settings = "os", "arch", "compiler"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    requires = "OpenSSL/1.1.1@conan/stable"
    source_folder = "net-snmp"
    exports = "net-snmp.patch"

    def configure(self):
        self.options["OpenSSL"].shared = True

    def system_requirements(self):
        self.global_system_requirements=True

    def source(self):
        git = tools.Git(folder="net-snmp")
        git.clone("/home/parallels/net-snmp-5.8", "master")
        if self.settings.os == "Windows":
            tools.patch(patch_file="net-snmp.patch", base_path=os.path.join(os.getcwd(), "net-snmp"))

    def linux_build(self):
        env_build = AutoToolsBuildEnvironment(self)
        configure = "./configure --with-default-snmp-version=3 \
        --with-sys-contact=@@no.where --with-sys-location=Unknown \
        --with-logfile=/var/log/snmpd.log \
        --with-persistent-directory=/var/net-snmp \
        --prefix=%s" % (os.path.join(self.source_folder, "net-snmp"))

        with tools.chdir(os.path.join(self.source_folder, "net-snmp")):
            self.run("chmod 755 configure")
            self.run(configure)
            env_build.make()
            env_build.install()


    def windows_build(self):
        os.environ['OPENSSL_INCLUDE_PATH'] = self.deps_cpp_info["OpenSSL"].include_paths[0]
        os.environ['OPENSSL_LIB_PATH'] = self.deps_cpp_info["OpenSSL"].lib_paths[0]
        config_command = "perl build.pl"
        self.output.warn(config_command)
        with tools.chdir(os.path.join(self.source_folder, "net-snmp\\win32")):
            self.run(config_command, win_bash=True)
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
