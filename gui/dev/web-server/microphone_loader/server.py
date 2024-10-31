import os
import random
import string
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import wave
import uuid
import gc
from opus.decoder import Decoder as OpusDecoder
from tornado.options import define, options

define("port", default=8888, type=int)

class OpusDecoderWS(tornado.websocket.WebSocketHandler):
    def open(self):
        print('new connection')
        self.initialized = False

    def my_init(self, msg):
        print(msg)
        rate, is_encoded, op_rate, op_frm_dur = [int(i) for i in msg.split(',')]
        #rate : actual sampling rate
        #op_rate : the rate we told opus encoder
        #op_frm_dur : opus frame duration
        
        filename = f'{str(uuid.uuid4())}.wav'
        wave_write = wave.open(filename, 'wb')
        wave_write.setnchannels(1)
        wave_write.setsampwidth(2)  # int16, even when not encoded
        wave_write.setframerate(rate)

        if self.initialized:
            self.wave_write.close()

        self.is_encoded = is_encoded
        self.decoder = OpusDecoder(op_rate, 1)
        self.frame_size = op_frm_dur * op_rate
        self.wave_write = wave_write
        self.initialized = True

    def on_message(self, data):
        if str(data).startswith('m:'):
            self.my_init(str(data[2:]))
        elif self.is_encoded:
            pcm = self.decoder.decode(data, self.frame_size, False)
            self.wave_write.writeframes(pcm)
            gc.collect()  # force garbage collector
        else:
            self.wave_write.writeframes(data)

    def on_close(self):
        if self.initialized:
            self.wave_write.close()
        print('connection closed')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        if 'file1' not in self.request.files:
            self.finish("No file uploaded")
            return
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = random.choice(string.ascii_lowercase + string.digits)
        final_filename = fname + extension
        with open(f"uploads/{final_filename}", 'wb') as output_file:
            output_file.write(file1['body'])
        self.finish(f"File {final_filename} is uploaded")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', OpusDecoderWS),
            (r'/', MainHandler),
            (r'/upload', UploadHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'www'})
        ]
        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "www"),  # путь к шаблонам
            "static_path": os.path.join(os.path.dirname(__file__), "www"),    # путь к статическим файлам
        }
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    print(f'HTTP server started on port {options.port}')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
