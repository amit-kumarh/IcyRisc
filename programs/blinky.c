#define BLINK_TIME 10 // ms

int main() {
  int *led_addr = (int *)0xFFFFFFFF;
  int *millis_addr = (int *)0xFFFFFFF4;
  int target;
  *led_addr = 1;
  while (1) {
    target = *millis_addr + BLINK_TIME;
    while (*millis_addr < target) {
    }
    *led_addr = !(*led_addr);
  }
}
