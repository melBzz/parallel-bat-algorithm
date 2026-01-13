CC      = gcc
MPICC   = mpicc
CFLAGS  = -Wall -O2 -Iinclude
LIBS    = -lm
OMPFLAGS = -fopenmp

SRC_DIR = src
OBJ_DIR = obj
INC_DIR = include

# Core objects (shared)
CORE_OBJS = $(OBJ_DIR)/bat_core.o $(OBJ_DIR)/bat_utils.o $(OBJ_DIR)/bat_rng.o

# Targets
SEQ_TARGET = sequential
OMP_TARGET = openmp_bat
MPI_TARGET = mpi_bat

all: $(SEQ_TARGET)

# Sequential
$(SEQ_TARGET): $(OBJ_DIR)/sequential.o $(CORE_OBJS)
	$(CC) -o $@ $^ $(LIBS)

# OpenMP
openmp: $(OMP_TARGET)
$(OMP_TARGET): $(OBJ_DIR)/openmp_bat.o $(CORE_OBJS)
	$(CC) $(OMPFLAGS) -o $@ $^ $(LIBS)

# MPI
mpi: $(MPI_TARGET)
$(MPI_TARGET): $(OBJ_DIR)/mpi_bat.o $(CORE_OBJS)
	$(MPICC) -o $@ $^ $(LIBS)


# Object rules
$(OBJ_DIR)/bat_core.o: $(SRC_DIR)/bat_core.c $(INC_DIR)/bat.h $(INC_DIR)/bat_utils.h
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/bat_utils.o: $(SRC_DIR)/bat_utils.c $(INC_DIR)/bat.h $(INC_DIR)/bat_utils.h
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/bat_rng.o: $(SRC_DIR)/bat_rng.c $(INC_DIR)/bat_rng.h
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/sequential.o: $(SRC_DIR)/sequential.c $(INC_DIR)/bat.h $(INC_DIR)/bat_utils.h
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Note: OpenMP object needs -fopenmp
$(OBJ_DIR)/openmp_bat.o: $(SRC_DIR)/openmp_bat.c $(INC_DIR)/bat.h $(INC_DIR)/bat_utils.h
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) $(OMPFLAGS) -c $< -o $@

# Note: MPI object needs mpicc
$(OBJ_DIR)/mpi_bat.o: $(SRC_DIR)/mpi_bat.c $(INC_DIR)/bat.h $(INC_DIR)/bat_utils.h
	@mkdir -p $(OBJ_DIR)
	$(MPICC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ_DIR)/*.o $(SEQ_TARGET) $(OMP_TARGET) $(MPI_TARGET)

.PHONY: all clean openmp mpi
