from db import run_query

def update_course_slots(color_map):
    # Daftar slot waktu nyata (bisa diubah sesuai kebutuhan)
    slots = [
        ("Senin", "07:00-08:30"),
        ("Senin", "08:00-09:30"),
        ("Senin", "09:30-11:00"),
        ("Senin", "11:00-12:30"),
        ("Selasa", "07:00-08:30"),
        ("Selasa", "08:00-09:30"),
        ("Selasa", "09:30-11:00"),
        ("Selasa", "11:00-12:30"),
        ("Rabu", "07:00-08:30"),
        ("Rabu", "08:00-09:30"),
        ("Rabu", "09:30-11:00"),
        ("Rabu", "11:00-12:30"),
        ("Kamis", "07:00-08:30"),
        ("Kamis", "08:00-09:30"),
        ("Kamis", "09:30-11:00"),
        ("Kamis", "11:00-12:30"),
        ("Jumat", "07:00-08:30"),
        ("Jumat", "08:00-09:30"),
        ("Jumat", "09:30-11:00"),
        ("Jumat", "11:00-12:30"),
    ]
    for course_id, color in color_map.items():
        idx = int(color) - 1
        if idx < len(slots):
            day, time_slot = slots[idx]
            schedule = f"{day} {time_slot}"
        else:
            day, time_slot, schedule = "", "", ""
        run_query("MATCH (c:Course {id: $id}) SET c.color = $color, c.day = $day, c.time_slot = $time_slot, c.schedule = $schedule", {
            'id': course_id, 'color': str(color), 'day': day, 'time_slot': time_slot, 'schedule': schedule
        }) 