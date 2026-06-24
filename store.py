def get_all_articles(conn) -> list[Article]:
    """Retrieve all articles from database"""
    cursor = conn.execute("""
        SELECT title, url, source, published_at 
        FROM articles 
        ORDER BY published_at DESC
    """)
    return [
        Article(
            title=row[0],
            url=row[1],
            source=row[2],
            published_at=datetime.fromisoformat(row[3])
        )
        for row in cursor.fetchall()
    ]
