"""all the imports i needed to use. Tkinter for gui. bs4(BeautifulSoup) was the meat and was used to get info from the website along with requests to download the site in the first place. Pickle was used to store data in text files. os was to check the if the files were empty"""
from tkinter import *
import bs4
import requests
import pickle
import os

"""i used this class to easily store the data in a later array. Since the info for every movie had the same arguments i could have a general class for them. The aguments are title, audienceScore, criticScore, and synopsis """
class Movie(object):
    def __init__(self, title = "", audienceScore = "", criticScore = "", synopsis = ""):
        self.title = title
        self.audienceScore = audienceScore
        self.criticScore = criticScore
        self.synopsis = synopsis
"""this class was the controller frame and was used to communicate between frames. Mostly to switch between frames."""
class ogFrame(Tk):
    def __init__(self):
        Tk.__init__(self)
        container = Frame(self)
        #creating the base frame
        container.pack(side="top", fill="both", expand=True)

        #creating a dictionary to store all frames and get them easily
        self.frames = {}

        #this loop will run through each window on startup and then add them to the dictionary above and also grid them so they can be drawn
        for F in (Window1, Window2, Window4):

            frame = F(parent = container,controller = self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        #shows the first window on startup
        self.show_frame(Window1)

    #this will be used to later switch between frames. it takes an argument so that when i call it later it i can put in whichever window i want to and raise it to the front so it is the only visible one
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
#first window class is subclass of the tkinter class Frame
class Window1(Frame):
    #initialize the parent, which is equal to the container in the ogFrame, and then the controller which references self in the ogFrame class.
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        #define the controller to use
        self.controller = controller

        #open a file called rottentomatoes.txt that will be used to store all movie data
        self.file = open("rottentomatoes.txt", "rb")

        #create an array for the movie data to go into
        self.movies = []

        #Since pickle.load does only the first line and I must call it again for the next line, I can use a loop to keep loading each line into the movies array and then if it cant load anymore, raising an exception, the loop breaks
        while True:
            try:
                self.movies.extend(pickle.load(self.file))
            except(EOFError):
                break
        #then close the file to save it
        self.file.close()

        #i had issues getting the entry of this window to window 2 so i made an array to store it and then dump it into a file further down
        self.currentEntry = []
        self.headerFont = ("Helvetica", "16", "bold italic")

        #add all the elements of the window
        self.addSelections()
        self.addLabels()
        self.addEntryBox()
        self.addButtons()

    def addLabels(self):
        #header
        Label(self, text='Find a Movie!', font=self.headerFont).grid(row=0, columnspan=2, sticky='NWE', padx=10)

        #question and instructions
        Label(self, text='What movie would you like to see? (You might need to enter the year)',wraplength=200).grid(row=1, column=1, sticky='WE')

    def addButtons(self):
        #search button that calls a function siteChoice
        self.btnSearch = Button(self, text="Search")
        self.btnSearch.grid(row=3, column=1)
        self.btnSearch["command"] = self.siteChoice

        #a button to look at movies that you have searched before(info is gathered from a text file)
        #uses lambda so the command can call show_frame and pass an argument to it
        btnPrvsMovies = Button(self, text="View Previously Searched Movies", command=lambda: self.controller.show_frame(Window4))
        btnPrvsMovies.grid(row=5, column=1)

    def addEntryBox(self):
        #create the entry box
        self.inpMovie = Entry(self)
        self.inpMovie.grid(row=2, column=1)

    def siteChoice(self):
       #get the entry that is currently in the box and make a new variable out of it
       #then strip the spaces on the side and replace spaces in between with _
       #this will get the format that rottentomatoes.com uses for its url of movies(seen later)
       self.newInpMovie = self.inpMovie.get()
       self.newInpMovie = self.newInpMovie.strip().replace(' ', '_')

       #encodes the input into a bytes-like object. Explained later
       self.bitesizedMovie = str.encode(self.inpMovie.get())

       #this is where i add the currentEntry to a file. It will always overwrite the old file so that it is up to date when it is used later.
       #only inputs the title because thats all i need to find the right movie in the other text file
       self.currentEntry.extend([Movie(self.inpMovie.get(),'','','')])
       file = open("currentSearch.txt", "wb")
       pickle.dump(self.currentEntry, file)
       file.close()

       #this if statement might be useless right now because there is only one option even though others are listed.
       #i had planned on adding the other options but i felt it more important to get one site down and all the data useable first.
       #Did not have time to do the others.
       if self.var.get() == self.OPTIONS[0]:
           #if you dont enter anything it wont go on
           if self.inpMovie.get() == '' :
               nothing = Label(self,text="You didn't enter anything.")
               nothing.grid(row=4, column=1)
               pass
           #continue with operations as usual otherwise.
           else:
               #set a variable 'res' equal to the download of the website with the users updated input input into the url
               res = requests.get('https://www.rottentomatoes.com/m/{}'.format(self.newInpMovie))

               #set a variable that will use BeautifulSoup to parse the download text with html
               tomatoSoup = bs4.BeautifulSoup(res.text, 'html.parser')

               #i made this to select the <div> tags that contain the <h1> tag
               #this will contain the 404 error on rottentomatoes.com
               invalidElems = tomatoSoup.select('div h1')

               #There are a lot of edge cases that wont return 404 or anything thats easy to check.
               #if i had more time i could try adding a timer check that passes if it takes too long to find the url
               if '404' in invalidElems[0].getText():

                   #create a label that informs the user they messed up and that proper spacing is required
                   error = Label(self, text='Sorry, could not find that movie. \nMake sure you use proper spacing.')
                   error.grid(row=4, column=1)

                   #clear the entry field of any characters
                   self.inpMovie.delete(0, END)
               #time for the meat
               else:
                   #this will find all <div> tags with the class 'audience-score meter'
                   audienceScore = tomatoSoup.find_all('div',class_='audience-score meter')

                   #then I get the first text found in that class
                   #the string had a bunch of '\n' and then 'liked it' but i just wanted the number so i removed the extra shit
                   audienceScore = audienceScore[0].getText().replace('\n', '').replace('liked it', '')

                   #find all <div> tags with class 'critic-score meter'
                   criticScore = tomatoSoup.find_all('div', class_='critic-score meter')

                   #the text had '\n's so i got rid of them
                   criticScore = criticScore[0].getText().replace('\n', '')

                   #find all <div> tags with the class 'movie_synopsis clamp clamp-6'
                   synopsis = tomatoSoup.find_all('div', class_='movie_synopsis clamp clamp-6')

                   #the text wasnt didnt print as anything weird here so I just had to get it
                   synopsis = synopsis[0].getText()

                   #add the all this info as an instance of the class Movie to the array movies
                   self.movies.extend([Movie(self.inpMovie.get(), audienceScore, criticScore, synopsis)])

                   #used to keep track of if the movie entered already existed in the file as to not add duplicates
                   exists = False

                   #this checks if the file is empty. if it is change exists to equal True to stay consistent with the later if else statements
                   if os.stat("rottentomatoes.txt").st_size == 0:
                       exists == True
                       pass

                   #otherwise do this
                   else:

                       #this opens a file as 'file' then allows you to do operations with it. it will automatically close once you leave it
                       #this was nice
                       with open("rottentomatoes.txt", "rb" , 0) as file:
                           #search through each line of the file
                           for line in file:
                               #so here is that variable again. Since it is reading in bytes i had to convert the entry into a bytes-like object.
                               #this will check if that entry is in the line
                               if self.bitesizedMovie in line:

                                   #the entry was there so set exists=true so that it wont add the item down there
                                   exists = True

                                   #call the controller(ogFrame) and then call show_frame with the argument of Window2 to switch to the second window
                                   self.controller.show_frame(Window2)

                                   """Add stuff that takes the info gotten from search and create a new frame with that info. since it is already in the file if the program is here then all that would be left to do is take the current search results and use those."""

                   if exists == True:
                       pass
                   else:
                        file = open("rottentomatoes.txt", "wb")
                        pickle.dump(self.movies, file)
                        file.close()
                        self.controller.show_frame(Window2)
                        """Switch windows down here to the next window and generate the different labels and stuff based on info gathered here"""
       elif self.var.get() == self.OPTIONS[1]:
           """Need to add basically the same thing as rottentomatoes but specific to Flixster"""
       elif self.var.get() == self.OPTIONS[2]:
           """Need to add code to scrape and go to next window based on if they picked Fandango"""

    def addSelections(self):
        self.OPTIONS = [
            "Rotten Tomatoes",
            "Flixster",
            "Fandango"
        ]

        self.var = StringVar()
        self.var.set(self.OPTIONS[0])

        self.drpDwn = OptionMenu(self, self.var, *self.OPTIONS)
        self.drpDwn.grid(row = 2, column = 2, sticky = 'W')

class Window2(Window1):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.headerFont2 = ("Helvetica", "16", "bold italic")
        #self.addSearchBox
        self.getResults()

    def addButtons2(self):
        self.prvs = Button(self, text="View your previously searched movies.",command=lambda:self.controller.show_frame(Window4))
        self.prvs.grid(row=3, column=1)
    def getResults(self):
        self.btnResults = Button(self, text ="get results")
        self.btnResults.pack()
        self.btnResults["command"] = self.createDepElems
    def createDepElems(self):
        self.btnResults.destroy()
        self.addButtons2()
        if os.stat("currentSearch.txt").st_size == 0:
            pass
        else:
            file = open("currentSearch.txt", "rb+")
            searchedMovie = pickle.load(file)
            for l in searchedMovie:
                currentMovieTitle = Label(self, text=l.title, font=self.headerFont2)
                currentMovieTitle.grid(row=0,columnspan=3,sticky="NWE")
            file.close()
            file = open("rottentomatoes.txt","rb")
            searchedMov = pickle.load(file)

            for lel in searchedMov:
                if lel.title == currentMovieTitle.cget("text"):
                    currentAudienceScore = Label(self, text="Audience Score: {}".format(lel.audienceScore))
                    currentAudienceScore.grid(row=1,column=0, sticky="W")

                    currentCriticScore = Label(self, text="Critic Score: {}".format(lel.criticScore))
                    currentCriticScore.grid(row=1, column=2, sticky="E")

                    currentSynopsis = Label(self, text="Synopsis: {}".format(lel.synopsis), wraplength=200)
                    currentSynopsis.grid(row=2, column=1, sticky="EW")

class Window4(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.crrntSelection = []
        self.getList()
    def getList(self):
        self.lstBtn = Button(self, text="Get List")
        self.lstBtn.pack(side=TOP)
        self.lstBtn["command"] = self.addListBox
    def addScrollBar(self):
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)
    def srchSelection(self):
        file = open("rottentomatoes.txt","rb")
        listSelection = pickle.load(file)

        for boo in listSelection:
            if boo.title == self.listbox.get(ACTIVE):
                self.crrntSelection.extend([Movie(boo.title,'','','')])
                file = open("currentSearch.txt", "wb")
                pickle.dump(self.crrntSelection, file)
                file.close()

                self.controller.show_frame(Window2)
    def addListBox(self):
        self.addScrollBar()
        self.listbox = Listbox(self, yscrollcommand=self.scrollbar.set, selectmode=SINGLE)
        self.listbox.pack()
        self.scrollbar.config(command=self.listbox.yview)
        self.srchSelection()
        self.addSearchButton()
        file = open("rottentomatoes.txt","rb")
        allMovies = pickle.load(file)
        for lul in allMovies:
            self.listbox.insert(END,lul.title)
    def addSearchButton(self):
        self.srchBtn = Button(self, text="Search Current Selection")
        self.srchBtn.pack(side=BOTTOM)
        self.srchBtn["command"] = self.srchSelection
root = ogFrame()
root.mainloop()
