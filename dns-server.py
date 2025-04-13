import socketserver
import dns.message
import dns.resolver
import dns.rdatatype
import ipaddress

BLACKLIST_FILE = "blacklist.txt"

# Diccionario: {redireccion_ip: [lista de IPs o rangos]}
REDIRECCION_MAP = {}

def cargar_lista_negra_avanzada():
    current_redirect_ip = None
    with open(BLACKLIST_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith(":"):
                current_redirect_ip = line[:-1]
                REDIRECCION_MAP[current_redirect_ip] = []
            else:
                try:
                    if '/' in line:
                        REDIRECCION_MAP[current_redirect_ip].append(ipaddress.ip_network(line, strict=False))
                    else:
                        REDIRECCION_MAP[current_redirect_ip].append(ipaddress.ip_address(line))
                except ValueError:
                    print(f"Formato inválido en blacklist: {line}")

def buscar_redireccion(ip):
    ip_obj = ipaddress.ip_address(ip)
    for redirect_ip, reglas in REDIRECCION_MAP.items():
        for regla in reglas:
            if isinstance(regla, ipaddress._BaseNetwork):
                if ip_obj in regla:
                    return redirect_ip
            elif ip_obj == regla:
                return redirect_ip
    return None

cargar_lista_negra_avanzada()

class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        try:
            request = dns.message.from_wire(data)
        except Exception:
            return

        question = request.question[0]
        domain = str(question.name)
        qtype = dns.rdatatype.to_text(question.rdtype)

        try:
            response = dns.resolver.resolve(domain, qtype)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            respuesta_final = dns.message.make_response(request)
            socket.sendto(respuesta_final.to_wire(), self.client_address)
            return

        respuesta_final = dns.message.make_response(request)

        if qtype == 'A':
            redirect_ip = None
            for rdata in response:
                match = buscar_redireccion(rdata.address)
                if match:
                    redirect_ip = match
                    break

            if redirect_ip:
                respuesta_final.answer.append(
                    dns.rrset.from_text(domain, 60, 'IN', 'A', redirect_ip)
                )
            else:
                for rdata in response:
                    respuesta_final.answer.append(
                        dns.rrset.from_text(domain, 60, 'IN', 'A', rdata.address)
                    )
        else:
            for rdata in response:
                respuesta_final.answer.append(
                    dns.rrset.from_text(domain, 60, 'IN', qtype, str(rdata))
                )

        socket.sendto(respuesta_final.to_wire(), self.client_address)

if __name__ == "__main__":
    with socketserver.UDPServer(("", 53), DNSHandler) as server:
        print("Servidor DNS personalizado iniciado en el puerto 53")
        server.serve_forever()
