#include <iostream>
#include <net-snmp/net-snmp-config.h>
int main() {
    std::cout << NETSNMP_AGENTID << std::endl;
    return 0;
}
