from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conlist
import math, json

app = FastAPI()

# Set allowed origins
origins = [
    "http://localhost:3000",
    "http://compucar.io/"
]

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],  # or restrict to ["GET", "POST"] etc.
    allow_headers=["*"],
)


# Just pass the list length directly in v2
class InputData(BaseModel):
    values: conlist(item_type=int, min_length=16, max_length=16)

def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0  # Avoid division by zero
    return dot_product / (norm1 * norm2)

def find_k_nearest_neighbors(data_vectors, input_vector, k=10):
    similarities = []

    for index, vec in enumerate(data_vectors):
        sim = cosine_similarity(input_vector, vec)
        similarities.append((index, sim))

    # Sort by similarity score in descending order
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top k neighbors
    return similarities[:k]
    
def run_my_script(values: list[int]) -> str:
        
    with open('carScores.json', 'r') as file:
        data = json.load(file)

    # extract only feature values (feature1 to feature16)
    car_data_vectors = [
        [entry[f"feature{i}"] for i in range(1, 17)]
        for entry in data
    ]

    # car names so we can map the suggested vector to the car
    car_name_vectors = [
        f"{entry['make']} {entry['model']} {entry['body_style']}"
        for entry in data
    ]
       
    input = values

    # count number of 0's in input
    # if more than 10 0's, 1/3 everything
    # between 6-9, 1/2 everything
    # 2 < x <= 5, 3/4 everything
    # else dont touch it
    count = 0

    for i in range(0,16):
        if(input[i] == 0):
            count += 1

    if(count >= 10):
        for i in range(0,16):
            input[i] = math.ceil(input[i]/3)
    elif(count >= 6):
        for i in range(0,16):
            input[i] = math.ceil(input[i]/2)
    elif(count >= 2):
        for i in range(0,16):
            input[i] = math.ceil((3*input[i])/4)

    # get nearest neighbors
    nearest = find_k_nearest_neighbors(car_data_vectors, input, k=10)

    return(car_name_vectors[nearest[0][0]], car_name_vectors[nearest[1][0]], car_name_vectors[nearest[2][0]], 
           car_name_vectors[nearest[3][0]], car_name_vectors[nearest[4][0]], car_name_vectors[nearest[5][0]], 
           car_name_vectors[nearest[6][0]], car_name_vectors[nearest[7][0]], car_name_vectors[nearest[8][0]], 
           car_name_vectors[nearest[9][0]])



@app.post("/run-script")
async def run_script(data: InputData):
    output = run_my_script(data.values)
    return {"output": output}