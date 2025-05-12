import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

total_functional = {(0,0),(0,1),(1,0),(1,1)}
total_write = {4,5}
total_read = {0,1,2,3}
hits_functional = set()
hits_write = set()
hits_read = set()

@cocotb.test()
async def testorgatefullcoverage(dut):
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    dut.RST_N.value = 0
    await Timer(20, units="ns")
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    for A in (0, 1):
        for B in (0, 1):
            await waituntilfifosready(dut)
            await register_write(dut, 4, A) 
            hits_write.add(4)
            await register_write(dut, 5, B)  
            hits_write.add(5)
            await waitforoutputready(dut)
            y = await register_read(dut, 3)  
            hits_read.add(3)
            required = A | B
            assert y == required, f"or({A},{B}) = {required}, got {y}"
            hits_functional.add((A, B))
            await register_read(dut, 0) 
            await register_read(dut, 1)
            await register_read(dut, 2) 
            hits_read.update({0,1,2})
    functionalcoverage = len(hits_functional) / len(total_functional) * 100
    writtencoverage = len(hits_write) / len(total_write) * 100
    readingcoverage = len(hits_read) / len(total_read) * 100
    dut._log.info(f"Functional Coverage:{functionalcoverage:.2f} %")
    dut._log.info(f"Write Coverage:{writtencoverage:.2f} %")
    dut._log.info(f"Read Coverage:{readingcoverage:.2f} %")
    if functionalcoverage < 100 or writtencoverage < 100 or readingcoverage < 100:
        dut._log.warning("Not complete.")
    else:
        dut._log.info("Covered fully.")

async def waituntilfifosready(dut):
    while True:
        a_ready = await register_read(dut, 0)  
        b_ready = await register_read(dut, 1) 
        if a_ready and b_ready:
            break
        await RisingEdge(dut.CLK)

async def waitforoutputready(dut):
    while True:
        y_ready = await register_read(dut, 2)  
        if y_ready:
            break
        await RisingEdge(dut.CLK)

async def register_write(dut, address, data):
    dut.write_en.value = 1
    dut.write_address.value = address
    dut.write_data.value = data

    while not dut.write_rdy.value:
        await RisingEdge(dut.CLK)
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0
    await RisingEdge(dut.CLK)
    
async def register_read(dut, address):
    dut.read_en.value = 1
    dut.read_address.value = address
    while not dut.read_rdy.value:
        await RisingEdge(dut.CLK)
    await RisingEdge(dut.CLK)
    data = dut.read_data.value.integer
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)
    return data
