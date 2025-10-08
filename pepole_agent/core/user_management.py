import hashlib
from .auth_manager import SessionLocal, Profile ,chat_messages,eval_messages
def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()
def create_user(username, password):
    """Creates a new user in the database."""
    session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = session.query(Profile).filter(Profile.username == username).first()
        if existing_user:
            return None, "Username already exists."

        if not username or not password:
            return None, "Username and password cannot be empty."
        
        hashed_password = hash_password(password)
        new_user = Profile(username=username, password_hash=hashed_password)
        
        session.add(new_user)
        session.commit()
        
        return new_user, "User created successfully! Please log in."
    except Exception as e:
        session.rollback()
        return None, f"An error occurred: {e}"
    finally:
        session.close()

def verify_user(username, password):
    """Verifies a user's credentials."""
    session = SessionLocal()
    try:
        user = session.query(Profile).filter(Profile.username == username).first()
        
        if not user:
            return None, "Invalid username or password."

        hashed_password = hash_password(password)
        if user.password_hash == hashed_password:
            return user, "Login successful."
        else:
            return None, "Invalid username or password."
    finally:
        session.close()
def save_chat_message(user_id: str, sender: str, content: str):
    """Saves a new chat message to the database."""
    session = SessionLocal()
    try:
        new_message = chat_messages(
            user_id=user_id,
            sender=sender,
            content=content
        )
        session.add(new_message)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving message: {e}")
    finally:
        session.close()
def save_eval_resp(user_id: str, 
                    summary: str, 
                    score: float, 
                    score_reason: str, 
                    field_of_interest: str, 
                    issues_and_strengths: str,
                    github_link: str = None, 
                    linkedin_link: str = None, 
                    ):
    session = SessionLocal()
    try:
       
        existing_message = session.query(eval_messages).filter(
            eval_messages.user_id == user_id,
            eval_messages.field_of_interest == field_of_interest
        ).first()

        if existing_message:
            
            existing_message.summary += f"\n{summary}" 
            existing_message.score += score 
            existing_message.score_reason += f"\n{score_reason}"  
            if github_link:
                existing_message.github_link = github_link
            if linkedin_link:
                existing_message.linkedin_link = linkedin_link
            existing_message.issues_and_strengths += f"\n{issues_and_strengths}"  
            session.commit()
        else:
    
            new_message = eval_messages(
                user_id=user_id,
                summary=summary,
                score=score,
                score_reason=score_reason,
                github_link=github_link,
                linkedin_link=linkedin_link,
                field_of_interest=field_of_interest,
                issues_and_strengths=issues_and_strengths
            )
            session.add(new_message)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving message: {e}")
    finally:
        session.close()
def load_chat_history(user_id: str):
    """Loads all chat messages for a specific user from the database."""
    session = SessionLocal()
    try:
        messages = session.query(chat_messages).filter(chat_messages.user_id == user_id).order_by(chat_messages.timestamp).all()
        
        history = [{"role": msg.sender, "content": msg.content} for msg in messages]
        return history
    except Exception as e:
        print(f"Error loading history: {e}")
        return []
    finally:
        session.close()
def load_eval_data(user_id:str=None):
    session = SessionLocal()
    try:
        if user_id:
            print('user')
            messages = session.query(eval_messages).filter(eval_messages.user_id == user_id).order_by(eval_messages.timestamp).all()
        else:
            messages = session.query(eval_messages).order_by(eval_messages.timestamp).all()

        history = [{
                     "score": msg.score,
                     'summary':msg.summary,
                     'score_reason':msg.score_reason,
                     'field_of_interest':msg.field_of_interest.lower().strip(),
                     'user_id':msg.user_id,
                     'issues_and_strengths':msg.issues_and_strengths} for msg in messages]
        return history
    except Exception as e:
        print(f"Error loading history: {e}")
        return []
    finally:
        session.close()
def get_username(user_id:str):
    session = SessionLocal()
    user_name=session.query(Profile).filter(Profile.user_id == user_id).order_by(Profile.timestamp).all()
  
    return user_name[0].username