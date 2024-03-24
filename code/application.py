# Standard lib
import os

# Interface lib
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

# Mosaic lib
import mosaic

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Title
        self.title('Photomosaic')

        # Resolution
        self.rowconfigure(0, minsize=800, weight=1)
        self.columnconfigure(1, minsize=800, weight=1)
        
        main_frame = tk.Frame(self)

        self.log = tk.StringVar()
        self.log.set("En attente")

        ## Button to access input image, output image
        # and dataset
        label_in = tk.Label(main_frame, text='Image en entrée')
        label_out = tk.Label(main_frame, text='Image en sortie')
        label_data = tk.Label(main_frame, text='Dataset')
        label_log = tk.Label(main_frame, textvariable=self.log)

        self.text_in = tk.Entry(main_frame, width=79)
        self.text_out = tk.Entry(main_frame, width=79)
        self.text_data = tk.Entry(main_frame, width=79)

        button_in_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.open_file)
        button_out_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.save_file)
        button_data_location = tk.Button(main_frame,\
            text='Parcourir...', command=self.open_dir)

        button_build_mosaic = tk.Button(main_frame,\
            text='Construire la mosaïque', command=self.photomosaic)

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

        self.text_in.select_clear()
        self.text_in.insert(0, path)
        
    def open_dir(self):
        """Open a folder """

        path = askdirectory()

        if not path:
            return

        self.text_data.select_clear()
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

        self.text_out.select_clear()
        self.text_out.insert(0, path)

    def initialize_mosaic(self):
        """Create an instance of mosaic with 
        path in entries
        """
        in_location = self.text_in.get()
        out_location = self.text_out.get()
        data_location = os.path.join(self.text_data.get(), '*')
        print(data_location)

        self.mosaic = mosaic.Mosaic(in_location, out_location, data_location)

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
        self.update()

if __name__ == "__main__":
    app = Application()
    app.mainloop()