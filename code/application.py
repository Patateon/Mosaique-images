# Standard lib
import os
import time

# Interface lib
import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

# Mosaic & video lib
import mosaic
import video

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
        self.auto_resize = tk.IntVar()
        self.show_advanced = False

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
        button_advanced = tk.Button(main_frame,\
            text='Options avancées', command=self.advanced)

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
        
        button_advanced.grid(row=4, column=1, sticky='', pady=5)

        self.main_frame = main_frame
        main_frame.pack()


    def open_file(self):
        """Open a file for editing."""

        path = askopenfilename(
            filetypes=[\
                ('Image Files', '.png .jpg .jpeg .ppm .mp4 .webm .mkv .avi .mov .flv .gif'),\
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
                ('Image Files', '.png .jpg .jpeg .ppm .mp4 .webm .mkv .avi .mov .flv .gif'),\
                ('All Files', '*.*')\
            ],
        )

        if not path:
            return

        self.text_out.delete(0, 'end')
        self.text_out.insert(0, path)

    def advanced(self):
        """Show/Unshow the advanced options"""

        self.show_advanced = not self.show_advanced
        advanced_frame = tk.Frame(self.main_frame)
        
        if self.show_advanced:
            self.res_x = tk.Label(advanced_frame, text="Résolution X")
            self.res_y = tk.Label(advanced_frame, text="Résolution Y")
            self.size_x = tk.Label(advanced_frame, text="Taille Mosaïc X")
            self.size_y = tk.Label(advanced_frame, text="Taille Mosaïc Y")
            
            self.text_res_x = tk.Entry(advanced_frame, width=5)
            self.text_res_x.insert('end', '50')
            self.text_res_y = tk.Entry(advanced_frame, width=5)
            self.text_res_y.insert('end', '50')
            self.text_size_x = tk.Entry(advanced_frame, width=5)
            self.text_size_x.insert('end', '32')
            self.text_size_y = tk.Entry(advanced_frame, width=5)
            self.text_size_y.insert('end', '32')

            self.checkbox_auto_resize = tk.Checkbutton(self.main_frame, text='Auto resize',\
                variable=self.auto_resize, onvalue=1, offvalue=0)

            self.res_x.grid(row=0, column=0, sticky='ew', pady=5)
            self.text_res_x.grid(row=0, column=1, sticky='ew', pady=5)
            self.res_y.grid(row=0, column=2, sticky='ew', pady=5)
            self.text_res_y.grid(row=0, column=3, sticky='ew', pady=5)

            self.size_x.grid(row=1, column=0, sticky='ew', pady=5)
            self.text_size_x.grid(row=1, column=1, sticky='ew', pady=5)
            self.size_y.grid(row=1, column=2, sticky='ew', pady=5)
            self.text_size_y.grid(row=1, column=3, sticky='ew', pady=5)

            advanced_frame.grid(row=5, column=1, sticky='ew', pady=5)
            self.checkbox_auto_resize.grid(row=5, column=0, sticky='ew', pady=5)
            
        else:
            self.text_res_x.destroy()
            self.text_res_y.destroy()
            self.text_size_x.destroy()
            self.text_size_y.destroy()
            self.res_x.destroy()
            self.res_y.destroy()
            self.size_x.destroy()
            self.size_y.destroy()
            self.checkbox_auto_resize.destroy()
            advanced_frame.destroy()
            

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
    
        # Video handling 
        # Common video formats can be optimized to handle all video types
        video_formats = ('.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.gif') 
        if in_location.lower().endswith(video_formats):
            if self.show_advanced:
                # Get resolution & mosaic size values
                res_x = self.text_res_x.get()
                res_y = self.text_res_y.get()
                size_x = self.text_size_x.get()
                size_y = self.text_size_y.get()
                self.mosaic = video.Video(in_location, out_location, data_location,\
                                            auto_resize=self.auto_resize.get(),\
                                            target_res=(int(res_x), int(res_y)), mosaic_size=(int(size_x), int(size_y)))
            else:
                self.mosaic = video.Video(in_location, out_location, data_location)
        
        # Image handling
        else:    
            # Get resolution & mosaic size values
            if self.show_advanced:
                res_x = self.text_res_x.get()
                res_y = self.text_res_y.get()
                size_x = self.text_size_x.get()
                size_y = self.text_size_y.get()
                self.mosaic = mosaic.Mosaic(in_location, out_location, data_location,\
                                            fast=self.fast_b.get(), auto_resize=self.auto_resize.get(),\
                                            target_res=(int(res_x), int(res_y)), mosaic_size=(int(size_x), int(size_y)))
            else:
                self.mosaic = mosaic.Mosaic(in_location, out_location, data_location, fast=self.fast_b.get())

    def dataset(self):
        """Process the datast"""

        self.mosaic.process_dataset()

    def photomosaic(self):
        """Build the mosaic"""

        self.log.set("Contruction de la mosaïque en cours...")
        self.update()
        try:
            start = time.time()
            self.initialize_mosaic()
            self.dataset()
            self.mosaic.build_mosaic()
            print("Time taken : " + str(time.time() - start)[:4] + " s")
        except Exception as e:
            self.log.set("Erreur lors de l'initialisation de la mosaïque, vérifiez les chemins")
            print(e)
            return
            
        self.log.set("Contruction terminée !")
        self.show_result()
            
        
    def show_result(self):
        """Show the result image in the interface"""
        result_frame = tk.Frame(self.main_frame)

        image_in = Image.open(self.text_in.get())
        image_in = image_in.resize((300, 300), Image.LANCZOS)
        image_in = ImageTk.PhotoImage(image_in)
        self.panel1 = tk.Label(result_frame, image=image_in)
        self.panel1.image = image_in  # Keep a reference to prevent garbage collection
        self.panel1.grid(row=0, column=0, sticky='', pady=5)

        image_out = Image.open(self.text_out.get())
        image_out = image_out.resize((300, 300), Image.LANCZOS)
        image_out = ImageTk.PhotoImage(image_out)
        self.panel2 = tk.Label(result_frame, image=image_out)
        self.panel2.image = image_out  # Keep a reference to prevent garbage collection
        self.panel2.grid(row=0, column=1, sticky='', pady=5)

        result_frame.grid(row=6, column=1, sticky='', pady=5)

        self.update()

if __name__ == "__main__":
    app = Application()
    app.mainloop()