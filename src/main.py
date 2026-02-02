from time import time
from math import isclose
from textual import on, work
from textual.worker import Worker, get_current_worker
from textual.app import App
from textual.containers import Container
from textual.widgets import Static, Header, Footer, Digits, Input, Button, HelpPanel


class TimerApp(App):
    
    START = 'Start'
    STOP = 'Stop'
    
    COMMANDS=[] 
    CSS_PATH='timer-app.tcss' 
    
    def __init__(self):
        super().__init__()
        self.engaged = True
        self.paused = False
        
    def __engaged(self):
        try:
            timer_value = int(self.timer_input.value)
            self.engaged = True
            self.timer_input.disabled = True
            self.begin_timer(timer_value)
        except ValueError:
            self.notify('Timer value must be a number')
            
    def __finished(self):
        self.bell()
        
    def __disengaged(self):
        self.engaged = False
        self.timer_input.disabled = False
        
    def __paused(self):
        pass
        
    def __upaused(self):
        pass 
    
    def compose(self):
        with Container(id='main-container', name='Terminal Timer'):
            with Container(id='timer-container'):
                yield Digits(id='timer-display', value='')
                yield Input(id='timer-input', type='integer', placeholder='some number of seconds', validate_on=['changed'])
                with Container(id='timer-buttons'):
                    yield Button(id='timer-start', label='Start', variant='primary')
                    yield Button(id='timer-stop', label='Stop', variant='error')
            
    def on_mount(self):
        self.timer_display = self.query_one('#timer-display', Digits)
        self.timer_input = self.query_one('#timer-input', Input)
        self.timer_start = self.query_one('#timer-start', Button)
        self.timer_stop = self.query_one('#timer-stop', Button)
        
        self.__disengaged()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.label:
            case TimerApp.START:
                self.action_start_timer()
            case TimerApp.STOP:
                self.action_stop_timer()
            case _:
                pass
        
    def action_start_timer(self):
        if not self.engaged:
            self.__engaged()
    
    def action_stop_timer(self):
        if self.engaged:
            self.workers.cancel_all()
            self.__disengaged()
    
    @on(Input.Changed)
    def timer_input_changed(self, event: Input.Changed) -> None:
        if self.timer_display and self.timer_input:
            new_value = str(self.timer_input.value) 
            self.timer_display.update(new_value)
            
    @work(exclusive=True, thread=True)
    def begin_timer(self, timer_value: int) -> None:
        try:
            worker = get_current_worker()
            digits: Digits = self.timer_display
            counter = timer_value
            
            a = time()      # start of the function (you may consider this the last time)
            while counter >= 0:
                b = time()  # next time
                if isclose(b - a, 1, rel_tol=0.1):  # isn't that just the nicest little thing
                    digits.update(str(counter))
                    counter = counter - 1
                    a = b   # update the last time
                if worker.is_cancelled:
                    break
                
            if not worker.is_cancelled: # lazy way to prevent double calling, do I even care if that happens?
                self.__finished()
                self.__disengaged()
        except ValueError:
            self.notify('timer value cannot be empty')


if __name__ == '__main__':
    """
    Terminal arguments
    
    How long the timer shall run
    ...
    
    Yeah that is it really
    """
    app = TimerApp()
    app.run(inline=True)
