from flask import Flask, request
import numpy as np
import flasgger
from flasgger import Swagger
from pickle import load

app=Flask(__name__)
Swagger(app)

loaded_model = load(open('best_model.pkl', 'rb'))
poly = load(open('poly.pkl', 'rb'))
sc = load(open('scalar.pkl', 'rb'))


@app.route('/',methods=["Get"])
def predict():

    """House Price Prediction
    Note: Only for houses with Latitude Ranging from: 24.93 - 24.97 , Longitude: 121.47 - 121.54
    ---
    parameters:
        - name: House Age
          in: query
          type: number
          description: "0 - 43"
          required: true
        - name: Distance_to_the_nearest_MRT_station
          in: query
          type: number
          description: "24 - 4k"
          required: true
        - name: number_of_convenience_stores
          in: query
          type: number
          description: "0-10"
          required: true
        - name: Latitude
          in: query
          type: number
          description: "24.93-25"
          required: true
        - name: Longitude
          in: query
          type: number
          description: "121.47 - 121.57"
          required: true
    responses:
          200:
              description: The output values
    """
    l=[]
    i1=request.args.get('House Age')
    l.append(i1)
    i2=request.args.get('Distance_to_the_nearest_MRT_station')
    l.append(i2)
    i3=request.args.get('number_of_convenience_stores')
    l.append(i3)
    i4=request.args.get('Latitude')
    l.append(i4)
    i5=request.args.get('Longitude')
    l.append(i5)
    arr = np.array([l])
    arr = poly.transform(arr)
    scaled_arr = sc.transform(arr)
    p = round(loaded_model.predict(scaled_arr)[0][0],2)
    return "Price of the house per unit area: "+str(p)









if __name__=='__main__':
    app.run()
