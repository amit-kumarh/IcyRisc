#define BLINK_TIME 10 // us
#define LED_PTR ((volatile unsigned char *)0xFFFFFFFF)
#define MICROS_PTR ((volatile unsigned int *)0xFFFFFFF4)

int main() {
  int target;
  *LED_PTR = 255;
  while (1) {
    target = *MICROS_PTR + BLINK_TIME;
    while (*MICROS_PTR < target) {
    }
    *LED_PTR = *LED_PTR == 0 ? 255 : 0;
  }
}
