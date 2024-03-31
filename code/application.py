# Standard lib
import os

# Interface lib
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

# Mosaic lib
import mosaic

class Application(tk.Tk):

    """Basic application with tkinter"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Title
        self.title('Photomosaic')

        # Resolution
        self.rowconfigure(0, minsize=800, weight=1)
        self.columnconfigure(1, minsize=800, weight=1)
        
        # Initialize the main frame 
        self.scene_initializer()


    def scene_initializer(self):
        """ Load a main frame in the ugliest way possible """

        main_frame = tk.Frame(self)

        self.log = tk.StringVar()
        self.log.set("En attente")

        self.fast_b = tk.IntVar()

        ## Button to access input image, output image
        # and dataset
        label_in = tk.Label(main_frame, text='Image en entrée')
        label_out = tk.Label(main_frame, text='Image en sortie')
        label_data = tk.Label(main_frame, text='Dataset')
        label_log = tk.Label(main_frame, textvariable=self.log)

        self.text_in = tk.Entry(main_frame, width=79)
        self.text_out = tk.Entry(main_frame, width=79)
        self.text_data = tk.Entry(main_frame, width=79)

        # Path par défaut
        self.text_data.insert(0, \
            os.path.join('dataset', 'cifar-10-batches-py'))

        button_in_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.open_file)
        button_out_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.save_file)
        button_data_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.open_dir)

        button_build_mosaic = tk.Button(main_frame,\
            text='Construire la mosaïque', command=self.photomosaic)

        checkbox_fast = tk.Checkbutton(main_frame, text='Rapide',\
            variable=self.fast_b, onvalue=1, offvalue=0)

        label_in.grid(row=0, column=0, sticky='ew', pady=5)
        label_out.grid(row=1, column=0, sticky='ew', pady=5)
        label_data.grid(row=2, column=0, sticky='ew', pady=5)
        label_log.grid(row=3, column=1, sticky='ew', pady=5)

        self.text_in.grid(row=0, column=1, sticky='ew', pady=5)
        self.text_out.grid(row=1, column=1, sticky='ew', pady=5)
        self.text_data.grid(row=2, column=1, sticky='ew', pady=5)

        button_in_location.grid(row=0, column=2, sticky='ew', pady=5)
        button_out_location.grid(row=1, column=2, sticky='ew', pady=5)
        button_data_location.grid(row=2, column=2, sticky='ew', pady=5)
        button_build_mosaic.grid(row=3, column=2, sticky='ew', pady=5)

        checkbox_fast.grid(row=3, column=0, sticky='ew', pady=5)

        self.main_frame = main_frame
        main_frame.pack()


    def open_file(self):
        """Open a file for editing."""

        path = askopenfilename(
            filetypes=[\
                ('Image Files', '.png .jpg .jpeg .ppm'),\
                ('All Files', '*.*')\
            ]
        )

        if not path:
            return

        self.text_in.delete(0, 'end')
        self.text_in.insert(0, path)
        
    def open_dir(self):
        """Open a folder """

        path = askdirectory()

        if not path:
            return

        self.text_data.delete(0, 'end')
        self.text_data.insert(0, path)


    def save_file(self):
        """Save the current file as a new file."""

        path = asksaveasfilename(
            defaultextension='.png',
            filetypes=[\
                ('Image Files', '.png .jpg .jpeg .ppm'),\
                ('All Files', '*.*')\
            ],
        )

        if not path:
            return

        self.text_out.delete(0, 'end')
        self.text_out.insert(0, path)


    def initialize_mosaic(self):
        """Create an instance of mosaic with 
        path in entries
        """
        in_location = self.text_in.get()
        out_location = self.text_out.get()
        data_location = self.text_data.get()

        print(data_location)

        # Ignoble mais c'est pour vérifier si load cifar 10 ou un dossier
        if (os.path.basename(self.text_data.get()) != 'cifar-10-batches-py'):
            data_location = os.path.join(data_location, '*')

        self.mosaic = mosaic.Mosaic(in_location, out_location, data_location, fast=self.fast_b.get())

    def dataset(self):
        """Process the datast"""

        self.mosaic.process_dataset()

    def photomosaic(self):
        """Build the mosaic"""

        self.log.set("Contruction de la mosaïque en cours...")
        self.update()
        self.initialize_mosaic()
        
        self.dataset()

        self.mosaic.build_mosaic()
        self.log.set("Contruction terminée !")
        self.show_result()
        
    def show_result(self):
        """Show the result image in the interface"""
        
        path = Image.open(self.text_out.get())
        resized = path.resize((400, 400), Image.LANCZOS)
        img = ImageTk.PhotoImage(resized)
        self.panel = tk.Label(self.main_frame, image=img)
        self.panel.image = img  # Keep a reference to prevent garbage collection
        self.panel.grid(row=4, column=1, sticky='', pady=5)
        self.update()

if __name__ == "__main__":
    app = Application()
    app.mainloop()