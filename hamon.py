import tkinter as tk
import queue
import math

class Hamon(tk.Frame) :
    class Stone :
        r = 10
    class Tag :
        hamon = 'hamon'
        stone = 'stone'
    class Color :
        stone_normal    = '#0000ff'
        stone_enter     = '#000077'
        stone_disabled  = '#7777ff'
    def dist(x1,y1,x2,y2) :
        dx = x1-x2
        dy = y1-y2
        return math.sqrt(dx*dx+dy*dy)
    def dist_by_dict(d1,d2) :
        return Hamon.dist(d1['x'],d1['y'],d2['x'],d2['y'])
        
    def __init__(self, master=None) :
        tk.Frame.__init__(self, master)
        
        '''user specified parameters'''
        self.fps = 50
        self.hamon_upper_bound = 708
        self.stone_rest_time = 500 # ms
        self.hamon_speed_perf = 5
        '''calculated parameters'''
        self.stone_rest_fcnt = self.stone_rest_time * self.fps / 1000
        '''internal use'''
       # self.hamon_list = list()
        self.stone_info_dict = dict()
        self.hamon_info_dict = dict()
        self.fcnt = 0
        self.q = queue.PriorityQueue()
        
        self.canvas = tk.Canvas(self, width=500, height=500)
        self.backgroud = self.canvas.create_rectangle(0,0,500,500, 
                                     fill='white', width=0)
        self.canvas.tag_bind(self.backgroud, '<Button-1>', 
                             lambda event : self.create_stone(event.x, event.y))
        text = self.canvas.create_text(250, 250, state=tk.DISABLED, 
                                       font='Helvetica', fill='grey') 
        self.canvas.itemconfig(text, text='\
            Left click to put a stone.\n\
            Right click on a stone to increase its number.\n\
            Middle click on a stone to remove it.\n\
            Left click on a stone to generate a Hamon!\
        ')
#        self.canvas.bind('<1>', lambda event : self.canvas.itemconfig(text, text='Bravo!'), '+')
                             
        tk.Pack.config(self)
        self.canvas.pack()
        
        self.after(1000//self.fps, self.update)
    
    def f_after(self, fcnt, func, *args) :
        class q_elem :
            def __init__(self, fcnt, func, *args) :
                self.fcnt = fcnt
                self.func = func
                self.args = args
            def __lt__(self, other) :
                return self.fcnt < other.fcnt
#        print('in f_after:', fcnt+self.fcnt, func)
        self.q.put(q_elem(fcnt+self.fcnt, func, *args))
        
    def update(self) :
#        print('in update:', 'self.fcnt=%d'%self.fcnt)
        self.fcnt += 1
        for hamon in self.canvas.find_withtag(Hamon.Tag.hamon) :
            h_info = self.hamon_info_dict[hamon]
            if h_info['r'] < self.hamon_upper_bound :
                self.adjust_hamon_radius_by(hamon, self.hamon_speed_perf)
            else :
                self.canvas.delete(hamon)
        while not self.q.empty() :
            elem = self.q.get()
            if elem.fcnt > self.fcnt :
                self.q.put(elem)
                break
#            print(elem.fcnt, elem.func)
            elem.func()
        self.after(1000//self.fps, self.update)
        
            
    def create_circle(self, x, y, r, **conf) :
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **conf)
        
    def create_stone(self, x, y) :
        print('in create_stone')
        def set_num(new_num) :
            self.canvas.itemconfig(s_info['text_num'], text=('%d'%new_num)),
            s_info['_num'] = new_num
        s_info = {
            'x': x, 'y': y, 
            'make_hamon': lambda event=None : self.hit_stone(stone_item),
            'last_hamon_fcnt': -1000,
            '_num': 1,
            'set_num': set_num,
            ## the order of drawing is specified
            'oval_padding': self.create_circle(x, y, Hamon.Stone.r*2, 
                                               fill='white', width=0),
            'self': self.create_circle(x, y, Hamon.Stone.r, 
                                        tags=Hamon.Tag.stone,
                                        fill=Hamon.Color.stone_normal, 
                                        disabledfill=Hamon.Color.stone_disabled,
                                        activefill=Hamon.Color.stone_enter),
            }
        s_info['text_num']= self.canvas.create_text(x, y, text=('%d'%s_info.get('_num')), 
                                                fill='white', state=tk.DISABLED),
        self.canvas.lower(s_info['oval_padding'])
        self.canvas.lift(s_info['oval_padding'], self.backgroud)
        
        stone_item = s_info['self']
        self.stone_info_dict[stone_item] = s_info
        
        print(self.canvas.gettags(stone_item), stone_item)
        self.canvas.tag_bind(stone_item, '<Button-1>', s_info['make_hamon'])
        self.canvas.tag_bind(s_info['oval_padding'], '<Button>', lambda event : None)
        self.canvas.tag_bind(stone_item, '<Button-2>', 
                             lambda event : self.delete_stone(stone_item))
#        self.canvas.tag_bind(stone_item, '<Enter>',
#                             lambda event : self.capture_wheel(s_info))
#        self.canvas.tag_bind(stone_item, '<Leave>',
#                             lambda event : self.decapture_wheel())
        self.canvas.tag_bind(stone_item, '<Button-3>',
                             lambda event : s_info['set_num'](s_info['_num']+1))
        
        for hamon in self.canvas.find_withtag(Hamon.Tag.hamon) :
            h_info = self.hamon_info_dict[hamon]
            gap = Hamon.dist_by_dict(s_info, h_info)
            fgap = (gap-Hamon.Stone.r) / self.hamon_speed_perf
            fcnt = fgap + h_info['start_fcnt']
            if fcnt >= self.fcnt :
                '''not hamons that already past the stone'''
                self.f_after(fcnt-self.fcnt, s_info['make_hamon'])
        
        return stone_item
    
#    def capture_wheel(self, s_info) :
#        print('in capture_wheel')
##        ## wheel up for Linux
##        self.bind('<Button-4>', lambda event : print(s_info['_num']+1))
##        ## wheel down for Linux
##        self.bind('<Button-5>', lambda event : print(s_info['_num']-1))
##        ## mouse wheel for MacOS or Windows
##        self.bind('<MouseWheel>', 
##                  lambda event : print(s_info['_num']))
#        self.canvas.bind('<KeyPress-w>', lambda event : print(s_info['_num']+1))
#        self.bind('<KeyPress-s>', lambda event : print(s_info['_num']-1))
#    def decapture_wheel(self) :
#        print('in decapture_wheel')
##        ## wheel up for Linux
##        self.unbind('<Button-4>')
##        ## wheel down for Linux
##        self.unbind('<Button-5>')
##        ## mouse wheel for MacOS or Windows
##        self.unbind('<MouseWheel>')
#        self.unbind('<KeyPress-Up>')
#        self.unbind('<KeyPress-Down>')
        
    def delete_stone(self, stone) :
        s_info = self.stone_info_dict.get(stone)
        if not s_info : return
        self.canvas.delete(s_info['text_num'])
        self.canvas.delete(s_info['oval_padding'])
        self.canvas.delete(stone)
        self.stone_info_dict.pop(stone)
        '''event about @stone in self.q remain untouched, 
        since deleted stone can be ignored by self.hit_stone()'''
        
    def create_hamon(self, x, y, r) :
        print('in create_hamon:', x, y, r)
        hamon = self.create_circle(x, y, r, tags=Hamon.Tag.hamon)
        h_info = {
            'x':x, 'y':y, 'r':r,
            'start_fcnt': self.fcnt,
        }
        self.hamon_info_dict[hamon] = h_info
        
        for stone in self.canvas.find_withtag(Hamon.Tag.stone) :
            s_info = self.stone_info_dict[stone]
            gap = Hamon.dist_by_dict(h_info, s_info)
            if gap > Hamon.Stone.r :
                '''not itself's source stone'''
                fgap = (gap-Hamon.Stone.r) / self.hamon_speed_perf
                self.f_after(fgap, s_info['make_hamon'])
        
        print(hamon)
        return hamon
        
    def adjust_hamon_radius_by(self, hamon, dr) :
#        print('in adjust_hamon:', hamon, dr)
        self.hamon_info_dict[hamon]['r'] += dr
        x, y, r = [self.hamon_info_dict[hamon][key] for key in ('x', 'y', 'r')]
        self.canvas.coords(hamon, (x-r, y-r, x+r, y+r))
        
    def hit_stone(self, stone_item) :
#        print('in hit_stone:', 'stone_item=%d'%stone_item)
        s_info = self.stone_info_dict.get(stone_item)
        if not s_info : return
        if (self.canvas.itemcget(stone_item, 'state') != tk.DISABLED 
            and s_info['_num'] > 0) :
            new_num = s_info['_num'] - 1
            s_info['set_num'](new_num)
            if new_num > 0 :
                self.canvas.itemconfig(stone_item, state=tk.DISABLED)
                self.f_after(self.stone_rest_fcnt, 
                            lambda : self.canvas.itemconfig(stone_item, state=tk.NORMAL))
            else :
                self.canvas.itemconfig(stone_item, fill=Hamon.Color.stone_disabled)
            return self.create_hamon(s_info['x'], s_info['y'], Hamon.Stone.r)
    
    
        
app = Hamon()
app.master.title('hamon')
app.mainloop()