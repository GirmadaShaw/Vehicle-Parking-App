from backend import app , db
from backend.seed import seed_data


with app.app_context():
    db.create_all()
    seed_data()    

if __name__=='__main__':
    app.run(debug=True)
