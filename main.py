from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse

medias: list[dict] = [
    {"id": 1, "title": "Interstellar", "director": "Christopher Nolan"},
    {"id": 2, "title": "Transformers", "director": "Michael Bay"}
]

class RequestHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status_code = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def _parse_path(self):
        path = urlparse(self.path).path.strip("/")
        return path.split("/") if path else []

    def do_GET(self):

        path_parts = self._parse_path()

        if len(path_parts) == 1 and path_parts[0] == "medias":
            self._send_json(medias, 200)

        elif len(path_parts) == 2 and path_parts[0] == "medias":

            try:
                search_id = int(path_parts[1])
                found_media = None

                for media in medias:
                    if media["id"] == search_id:
                        found_media = media
                        break

                if found_media:
                    self._send_json(found_media, 200)
                else:
                    self._send_json({"Erreur": "Média non trouvé"}, 404)

            except ValueError:
                self._send_json({"Erreur": "L'ID doit être un entier"}, 400)

        else:
            self._send_json({"Erreur": "Route non trouvée"}, 404)

    def do_POST(self):
        
        if self.path == "/medias":

            try:
                data = self._read_json_body()
                new_media = {
                    "id": len(medias) + 1,
                    "title": data.get("title", "Sans titre"),
                    "director": data.get("director", "Non renseigné")
                }
                medias.append(new_media)
                self._send_json(new_media, 201)

            except json.JSONDecodeError:
                self._send_json({"Erreur": "Json invalide"}, 400)

        else:
            self._send_json({"Erreur": "Chemin non trouvé"}, 404)

    def do_DELETE(self):

        path_parts = self._parse_path()

        if len(path_parts) == 2 and path_parts[0] == "medias":
            try:
                search_id = int(path_parts[1])
                media_to_delete = None

                for media in medias:
                    if media["id"] == search_id:
                        media_to_delete = media
                        break

                if media_to_delete:
                    medias.remove(media_to_delete)
                    self._send_json({"Message :": f"Média {search_id} supprimé."}, 200)

                else:
                    self._send_json({"Erreur": "Média non trouvé"}, 404)

            except ValueError:
                self._send_json({"Erreur": "L'ID doit être un entier"}, 400)

        else:
            self._send_json({"Erreur": "Chemin non trouvé"}, 404)

def run_server():
    server_adress = ('localhost', 8080)
    httpd = HTTPServer(server_adress, RequestHandler)
    print("Serveur en cours d'éxécution sur http://localhost:8080")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Arrêt du serveur.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
    