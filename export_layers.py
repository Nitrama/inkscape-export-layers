#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil


class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--path", action="store", type="string", dest="path", default="~/", help="")
        self.OptionParser.add_option('-f', '--filetype', action='store', type='string', dest='filetype', default='jpeg', help='Exported file type')

    def effect(self):
        output_path = os.path.expanduser(self.options.path)
        curfile = self.args[-1]
        layers = self.get_layers(curfile)
        counter = 1

        for (layer_id, layer_label, layer_type) in layers:
            if layer_type == "fixed":
                continue

            show_layer_ids = [layer[0] for layer in layers if layer[2] == "fixed" or layer[0] == layer_id]

            if not os.path.exists(os.path.join(output_path)):
                os.makedirs(os.path.join(output_path))

            layer_dest_svg_path = os.path.join(output_path, "%s.svg" % layer_label)
            layer_dest_png_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))

            self.export_layers(curfile, layer_dest_svg_path, show_layer_ids)
            self.exportToPng(layer_dest_svg_path, layer_dest_png_path)

            if self.options.filetype == "jpeg":
                layer_dest_jpg_path = os.path.join(output_path, "%s_%s.jpg" % (str(counter).zfill(3), layer_label))
                self.convertPngToJpg(layer_dest_png_path, layer_dest_jpg_path)
                os.unlink(layer_dest_png_path)

            os.unlink(layer_dest_svg_path)
            counter += 1

    def export_layers(self, src, dest, show):
        """
        Export selected layers of SVG in the file `src` to the file `dest`.
        :arg  str    src:  path of the source SVG file.
        :arg  str   dest:  path to export SVG file.
        :arg  list  hide:  layers to hide. each element is a string.
        :arg  list  show:  layers to show. each element is a string.
        """
        for layer in self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS):
            layer.attrib['style'] = 'display:none'
            id = layer.attrib["id"]
            if id in show:
                layer.attrib['style'] = 'display:inline'

        self.document.write(dest)

    def get_layers(self, src):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        layers = []

        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            layer_id = layer.attrib["id"]
            layer_label = layer.attrib[label_attrib_name]

            if layer_label.startswith("[fixed] "):
                layer_type = "fixed"
                layer_label = layer_label[8:]
            elif layer_label.startswith("[export] "):
                layer_type = "export"
                layer_label = layer_label[9:]
            else:
                continue

            layers.append([layer_id, layer_label, layer_type])

        return layers

    def exportToPng(self, svg_path, output_path):
        command = "inkscape -C -e \"%s\" \"%s\"" % (output_path, svg_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    def convertPngToJpg(self, png_path, output_path):
        command = "convert \"%s\" \"%s\"" % (png_path, output_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


def _main():
    e = PNGExport()
    e.affect()
    exit()

if __name__ == "__main__":
    _main()
