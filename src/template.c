#include <zlib.h>
#include <stdio.h>
#include "kseq.h"
#include "uthash.h"

KSEQ_INIT(gzFile, gzread)

struct kmers {
    char key[255];                    /* key */
    char value[255];
    UT_hash_handle hh;                /* makes this structure hashable */
};

struct kmers *left  = NULL;            /* important! initialize to NULL */
struct kmers *right = NULL;            /* important! initialize to NULL */

void add_left(char *key, char *value) {
    struct kmers *s;

    HASH_FIND_STR(left, key, s);       /* id already in the hash? */
    if(s==NULL){
        s = malloc(sizeof(struct kmers));
        strcpy(s->key, key);
        strcpy(s->value, value);
        HASH_ADD_STR( left, key, s );  /* id: name of key field */
    }
}
void add_right(char *key, char *value) {
    struct kmers *s;

    HASH_FIND_STR(right, key, s);       /* id already in the hash? */
    if(s==NULL){
        s = malloc(sizeof(struct kmers));
        strcpy(s->key, key);
        strcpy(s->value, value);
        HASH_ADD_STR( right, key, s );  /* id: name of key field */
    }
}
struct kmers *find_left(char *kmer) {
    struct kmers *s;

    HASH_FIND_STR( left, kmer, s );  /* s: output pointer */
    return s;
}
struct kmers *find_right(char *kmer) {
    struct kmers *s;

    HASH_FIND_STR( right, kmer, s );  /* s: output pointer */
    return s;
}


void slice(const char *str, char *result, size_t start, size_t end){
    strncpy(result, str + start, end - start);
}


int main(int argc, char *argv[])
{
	gzFile fp;
	kseq_t *seq;
	int i,j,l;
	int len = 30;

	char buffer[255];


	if (argc < 3) {
		fprintf(stderr, "Usage: %s <one.fna> <two.fna>\n", argv[0]);
		return 1;
	}


	// GO THROUGH FIRST FILE AND FIND ALL POSSIBLE KMERS ON ENDS
	fp = gzopen(argv[1], "r");
	seq = kseq_init(fp);
	while ((l = kseq_read(seq)) >= 0) {
		// HEADER
		//printf("%c%s", seq->qual.l == seq->seq.l? '@' : '>', seq->name.s);
		//if (seq->comment.l) printf(" %s", seq->comment.s);
		//putchar('\n');

		// SEQUENCE
		for (i = 0; i < len; i++){
			slice(seq->seq.s, buffer, 0, i);
			add_left( buffer, buffer );
			slice(seq->seq.s, buffer, seq->seq.l - i, seq->seq.l);
			add_right( buffer, buffer );
		}
	}
	kseq_destroy(seq);
	gzclose(fp);

	// GO THROUGH OTHER FILE AND FIND ALL POSSIBLE KMERS ON ENDS
	fp = gzopen(argv[2], "r");
	seq = kseq_init(fp);
	while ((l = kseq_read(seq)) >= 0) {
		// HEADER
		//printf("%c%s", seq->qual.l == seq->seq.l? '@' : '>', seq->name.s);
		//if (seq->comment.l) printf(" %s", seq->comment.s);
		//putchar('\n');

		// SEQUENCE
		for (i = 0; i < len; i++){
			slice(seq->seq.s, buffer, 0, i);
			for (j = 0; j < i; j++){
				if(find_left(buffer))
					printf("match\n");
				buffer[j] = 'N';
			}
			slice(seq->seq.s, buffer, seq->seq.l - i, seq->seq.l);
			for (j = 0; j < i; j++){
				if(find_right(buffer))
					printf("match\n");
				buffer[j] = 'N';
			}
		}
	}
	kseq_destroy(seq);
	gzclose(fp);

	return 0;
}
