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
        self.hamon_upper_bound = 500
        self.stone_rest_time = 500 # ms
        self.hamon_speed_perf = 5
        '''calculated parameters'''
        self.stone_rest_fcnt = self.stone_rest_time * self.fps / 1000
        '''internal use'''
       # self.hamon_list = list()
        self.stone_info_dict = dict()
        self.hamon_info_dict = dict()
        self.fcnt = 0
        
        self.canvas = tk.Canvas(self, width=500, height=500)
        self.canvas.create_rectangle(0,0,500,500, 
                                     fill='white', tags='background')
        self.canvas.tag_bind('background', '<Button-1>', self.left_click)
        tk.Pack.config(self)
        self.canvas.pack()
        
        
        self.after(1000//self.fps, self.update)
    
    def left_click(self, event) :
        print('in left_click')
        obj_list = self.canvas.find_closest(event.x, event.y)
        print(obj_list)
        def find_stone_item() :
            return
            for obj in obj_list :
                print(self.canvas.gettags(obj))
                if Hamon.Tag.stone in self.canvas.gettags(obj) :
                    return obj
        stone_item = find_stone_item()
        print(stone_item)
        if stone_item == None :
            self.create_stone(event.x, event.y)
            
    def create_circle(self, x, y, r, **conf) :
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **conf)
        
    def create_stone(self, x, y) :
        print('in create_stone')
        stone_item = self.create_circle(x, y, Hamon.Stone.r, 
                                        tags=Hamon.Tag.stone,
                                        fill=Hamon.Color.stone_normal, 
                                        disabledfill=Hamon.Color.stone_disabled,
                                        activefill=Hamon.Color.stone_enter)
        s_info = {
            'x': x, 'y': y, 
            'q': queue.PriorityQueue(),
            'make-hamon': lambda event=None : self.create_hamon_with(stone_item),
            'last-hamon-fcnt': -1000,
            'num': 1,
        }
        self.stone_info_dict[stone_item] = s_info
        
        print(self.canvas.gettags(stone_item), stone_item)
        self.canvas.tag_bind(stone_item, '<Button-1>', s_info['make-hamon'])
        
        for hamon in self.canvas.find_withtag(Hamon.Tag.hamon) :
            h_info = self.hamon_info_dict[hamon]
            gap = Hamon.dist_by_dict(s_info, h_info)
            fgap = (gap-Hamon.Stone.r) / self.hamon_speed_perf
            fcnt = fgap + h_info['start-fcnt']
            if fcnt >= self.fcnt :
                '''not hamons that already past the stone'''
                s_info['q'].put((fcnt, s_info['make-hamon']))
        
        return stone_item
        
    def create_hamon(self, x, y, r) :
        print('in create_hamon:', x, y, r)
        hamon = self.create_circle(x, y, r, tags=Hamon.Tag.hamon)
        h_info = {
            'x':x, 'y':y, 'r':r,
            'start-fcnt': self.fcnt,
        }
        self.hamon_info_dict[hamon] = h_info
        
        for stone in self.canvas.find_withtag(Hamon.Tag.stone) :
            s_info = self.stone_info_dict[stone]
            q = s_info['q']
            gap = Hamon.dist_by_dict(h_info, s_info)
            if gap > Hamon.Stone.r :
                '''not itself's source stone'''
    #            q = queue.PriorityQueue()
                fgap = (gap-Hamon.Stone.r) / self.hamon_speed_perf
                q.put((fgap+self.fcnt, s_info['make-hamon']))
        
        print(hamon)
        return hamon
        
    def adjust_hamon_radius_by(self, hamon, dr) :
#        print('in adjust_hamon:', hamon, dr)
        self.hamon_info_dict[hamon]['r'] += dr
        x, y, r = [self.hamon_info_dict[hamon][key] for key in ('x', 'y', 'r')]
        self.canvas.coords(hamon, (x-r, y-r, x+r, y+r))
        
    def create_hamon_with(self, stone_item) :
        s_info = self.stone_info_dict[stone_item]
        last_fcnt = s_info['last-hamon-fcnt']
        if last_fcnt + self.stone_rest_fcnt <= self.fcnt :
            s_info['last-hamon-fcnt'] = self.fcnt
            self.canvas.itemconfig(stone_item, 
                                   state=tk.DISABLED)
            s_info['q'].put((self.fcnt + self.stone_rest_fcnt, 
                             lambda : self.canvas.itemconfig(stone_item, state=tk.NORMAL)))
            return self.create_hamon(s_info['x'], s_info['y'], Hamon.Stone.r)
    
    
    def update(self) :
#        print('in update')
        self.fcnt += 1
        for hamon in self.canvas.find_withtag(Hamon.Tag.hamon) :
            h_info = self.hamon_info_dict[hamon]
            if h_info['r'] < self.hamon_upper_bound :
                self.adjust_hamon_radius_by(hamon, self.hamon_speed_perf)
            else :
                self.canvas.delete(hamon)
        for stone in self.canvas.find_withtag(Hamon.Tag.stone) :
            s_info = self.stone_info_dict[stone]
            q = s_info['q']
#            q = queue.PriorityQueue()
            while not q.empty() :
                fcnt, f = q.get()
                if fcnt > self.fcnt :
                    q.put((fcnt, f))
                    break
#                self.create_hamon(s_info['x'], s_info['y'], Hamon.Stone.r)
                f()
#        self.canvas.update()
        self.after(1000//self.fps, self.update)
        
app = Hamon()
app.master.title('hamon')
app.mainloop()