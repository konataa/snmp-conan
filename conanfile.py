from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

class SnmpConan(ConanFile):
    name = "net-snmp"
    version = "5.8"
    license = "http://net-snmp.sourceforge.net/about/license.html"
    author = "Amina Ramazanova"
    description = "net-snmp package"
    topics = ("net-snmp", "snmp")
    settings = "os_build", "arch_build", "arch", "compiler"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    requires = "OpenSSL/1.1.1@conan/stable"
    source_folder = "net-snmp"
    exports = "net-snmp.patch"

    def configure(self):
        self.options["OpenSSL"].shared = True

    def source(self):
        git = tools.Git(folder="net-snmp")
        git.clone("C:\\Workspace\\net-snmp-5.8", "master")
        tools.patch(patch_file="net-snmp.patch", base_path=os.path.join(os.getcwd(), "net-snmp"))
    
    
    def build(self):
        os.environ['OPENSSL_INCLUDE_PATH'] = self.deps_cpp_info["OpenSSL"].include_paths[0]
        os.environ['OPENSSL_LIB_PATH'] = self.deps_cpp_info["OpenSSL"].lib_paths[0]
        config_command = "perl build.pl"
        self.output.warn(config_command)
        self.run_in_src(config_command)
    
    def run_in_src(self, command, show_output=False, win_bash=False):
        with tools.chdir(os.path.join(self.source_folder, "net-snmp\\win32")):
            self.run(command, win_bash=win_bash, output=True)
        self.output.writeln(" ")

    def package(self):
        self.copy("*.h", dst="include", src="net-snmp")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["netsnmp", "netsnmpagent", "netsnmpmibs", "netsnmptrapd"]