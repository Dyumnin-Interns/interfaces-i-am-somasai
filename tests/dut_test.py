import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep
from cocotb_bus.driver import BusDriver

def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"
    
@cocotb.test()
async def or_test(dut):
    global expected_value
    a = (0, 0, 1, 1)
    b = (0, 1, 0, 1)
    expected_value = (0, 1, 1, 1)
    dut.RST_N.value =  1 
    await Timer(1, 'ns')
    dut.RST_N.value = 0
    await Timer(1, 'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    adrv = InputDriver(dut, 'a', clk)
    adrv = InputDriver(dut, 'b', clk)
    OutputDriver(dut, 'y', dut.CLK, sb_fn)
    
    for i in range(4):
        adrv.append(a[i])
        bdrv.append(b[i])
    while len(expected_value)>0:
        await Timer(2, 'ns'))
        
class_InputDriver(BusDriver):
    _signals = ['rdy, 'en', 'data']

    def __init__(self,dut,name,clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk  
        
    async_def _driver_send(self,value,sync = True):
        if self.bus.rdy.value !=1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.data.value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
        
class_OutputDriver(BusDriver):
    _signals = ['rdy, 'en', 'data']

    def __init__(self,dut,name,clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
        self.callback = sb_callback
        self.append(0)
        
    async_def _driver_send(self,value,sync = True):
        while True:
          if self.bus.rdy.value != 1:
              await RisingEdge(self.bus.rdy)
          self.bus.en.value = 1
          await ReadOnly()
          self.callback(self.bus.data.value)
          await RisingEdge(self.clk)
          self.bus.en.value = 0
          await NextTimeStep()
