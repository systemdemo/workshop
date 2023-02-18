#include <systemd/sd-journal.h>

int main(int argc, char *argv[]) {
        sd_journal_print(LOG_INFO, "Hello from programmatic journal print!");
        return 0;
}