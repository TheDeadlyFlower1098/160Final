    teachers = [
        ('John Doe', 'Math'),
        ('Jane Smith', 'Science'),
        ('Jim Brown', 'History'),
        ('Alice Green', 'English'),
        ('Charlie White', 'Physics'),
        ('Eve Black', 'Biology'),
        ('Grace Blue', 'Chemistry'),
        ('Hank Grey', 'Geography'),
        ('Ivy Yellow', 'Art'),
        ('Jack Orange', 'Music')
    ]

    for i, (name, subject) in enumerate(teachers, start=1):
        user_id = i  # Manually assigning user_id
        conn.execute(
            text("INSERT INTO user (user_id, name, email, password, role) VALUES (:user_id, :name, :email, :password, 'Teacher')"),
            {"user_id": user_id, "name": name, "email": f"{name.split()[0].lower()}@school.com", "password": f"{name.split()[0].lower()}123"}
        )
        conn.execute(
            text("INSERT INTO teacher (teacher_id, subject) VALUES (:teacher_id, :subject)"),
            {"teacher_id": user_id, "subject": subject}
        )