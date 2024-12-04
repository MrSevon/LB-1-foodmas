from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import FileSystemLoader, Environment
import json
from urllib.parse import parse_qs

class MyHandler(SimpleHTTPRequestHandler):
    
    
    env = Environment(
        loader=FileSystemLoader('templates')
    )

    
    

    def do_GET(self):
        if self.path in ['/', '/delivery', '/bouquets', '/order', '/order-success']:
            self.handle_template(self.path)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/submit-order':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = parse_qs(post_data.decode('utf-8'))

                bouquet_id = data.get('bouquet_id', [''])[0]
                customer_name = data.get('customer_name', [''])[0]
                customer_phone = data.get('customer_phone', [''])[0]
                customer_address = data.get('customer_address', [''])[0]
                order_notes = data.get('order_notes', [''])[0]

                new_order = {
                    "bouquet_id": bouquet_id,
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_address": customer_address,
                    "order_notes": order_notes
                }
                self.save_order(new_order)

                self.send_response(302)
                self.send_header('Location', '/order-success')
                self.end_headers()
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")

    def handle_template(self, path):
        template_map = {
            '/': 'home.html',
            '/delivery': 'delivery.html',
            '/bouquets': 'bouquets.html',
            '/order': 'order.html',
            '/order-success': 'order-success.html'
        }
        template_name = template_map.get(path, 'home.html')
        try:
            template = self.env.get_template(template_name)

            context = {}
            if template_name == 'bouquets.html':
                with open('data.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    context['bouquets'] = data

            html_content = template.render(context)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def save_order(self, order):
        try:
            with open('orders.json', 'r+', encoding='utf-8') as file:
                orders = json.load(file)
                orders.append(order)
                file.seek(0)
                json.dump(orders, file, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            with open('orders.json', 'w', encoding='utf-8') as file:
                json.dump([order], file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    httpd.serve_forever()
