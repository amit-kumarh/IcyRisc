MEMORY
{
   BRAM (RWX) : ORIGIN = 0x00000000, LENGTH = 0x00001FFF
}

ENTRY(main)

SECTIONS {
    everything :
    {
        . = ALIGN(4);
        *(.*)
    } > BRAM
}
