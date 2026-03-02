#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* =========================
   EXPORT MACRO FOR WINDOWS
   ========================= */
#define EXPORT __declspec(dllexport)

/* =========================
   STRUCT DEFINITIONS
   ========================= */

struct Book {
    int id;
    char title[100];
    char author[100];
    int quantity;
    struct Book* next;
};

struct Book* head = NULL;

/* -------- STACK (Undo Delete) -------- */

struct Stack {
    struct Book book;
    struct Stack* next;
};

struct Stack* top = NULL;

/* -------- QUEUE (Issue Books) -------- */

struct Queue {
    int bookID;
    struct Queue* next;
};

struct Queue* front = NULL;
struct Queue* rear = NULL;

/* =========================
   FILE FUNCTIONS
   ========================= */

void saveToFile() {
    FILE *fp = fopen("library.txt", "w");
    struct Book *temp = head;

    while (temp != NULL) {
        fprintf(fp, "%d,%s,%s,%d\n",
                temp->id,
                temp->title,
                temp->author,
                temp->quantity);
        temp = temp->next;
    }

    fclose(fp);
}

void loadFromFile() {
    FILE *fp = fopen("library.txt", "r");
    if (fp == NULL) return;

    struct Book *newBook;

    while (!feof(fp)) {
        newBook = (struct Book*)malloc(sizeof(struct Book));
        if (fscanf(fp, "%d,[^,],[^,],%d\n",
                   &newBook->id,
                   newBook->title,
                   newBook->author,
                   &newBook->quantity) != 4) {
            free(newBook);
            break;
        }

        newBook->next = head;
        head = newBook;
    }

    fclose(fp);
}

/* =========================
   STACK FUNCTIONS
   ========================= */

void push(struct Book deletedBook) {
    struct Stack* newNode = (struct Stack*)malloc(sizeof(struct Stack));
    newNode->book = deletedBook;
    newNode->next = top;
    top = newNode;
}

void popUndo() {
    if (top == NULL) return;

    struct Book* newBook = (struct Book*)malloc(sizeof(struct Book));
    *newBook = top->book;
    newBook->next = head;
    head = newBook;

    struct Stack* temp = top;
    top = top->next;
    free(temp);

    saveToFile();
}

/* =========================
   QUEUE FUNCTIONS
   ========================= */

void enqueue(int id) {
    struct Queue* newNode = (struct Queue*)malloc(sizeof(struct Queue));
    newNode->bookID = id;
    newNode->next = NULL;

    if (rear == NULL) {
        front = rear = newNode;
    } else {
        rear->next = newNode;
        rear = newNode;
    }
}

int dequeue() {
    if (front == NULL)
        return -1;

    struct Queue* temp = front;
    int id = temp->bookID;

    front = front->next;
    if (front == NULL)
        rear = NULL;

    free(temp);
    return id;
}

/* =========================
   LIBRARY OPERATIONS
   ========================= */

EXPORT void addBook(int id, const char* title,
                    const char* author, int quantity) {

    struct Book* newBook = (struct Book*)malloc(sizeof(struct Book));

    /* Auto-generate ID */
    static int autoID = 1;
    newBook->id = autoID++;

    strcpy(newBook->title, title);
    strcpy(newBook->author, author);
    newBook->quantity = quantity;

    newBook->next = head;
    head = newBook;

    saveToFile();
}

EXPORT int deleteBook(int id) {
    struct Book *temp = head, *prev = NULL;

    while (temp != NULL) {
        if (temp->id == id) {

            if (prev == NULL)
                head = temp->next;
            else
                prev->next = temp->next;

            push(*temp);
            free(temp);
            saveToFile();
            return 1;
        }

        prev = temp;
        temp = temp->next;
    }

    return 0;
}

EXPORT int searchBook(int id, char* result) {
    struct Book* temp = head;

    while (temp != NULL) {
        if (temp->id == id) {
            sprintf(result, "ID:%d | %s | %s | Qty:%d",
                    temp->id,
                    temp->title,
                    temp->author,
                    temp->quantity);
            return 1;
        }
        temp = temp->next;
    }

    return 0;
}

EXPORT void displayBooks(char* buffer) {
    struct Book* temp = head;
    buffer[0] = '\0';

    while (temp != NULL) {
        char line[300];

        sprintf(line, "%d | %s | %s | %d\n",
                temp->id,
                temp->title,
                temp->author,
                temp->quantity);

        strcat(buffer, line);
        temp = temp->next;
    }
}

EXPORT void undoDelete() {
    popUndo();
}

EXPORT void issueBook(int id) {
    enqueue(id);
}

EXPORT int returnBook() {
    return dequeue();
}

/* =========================
   INITIALIZATION
   ========================= */

EXPORT void initializeLibrary() {
    loadFromFile();
}




//To run 
//gcc -shared -o library.dll library.c
//then in main.py file 
//use python main.py