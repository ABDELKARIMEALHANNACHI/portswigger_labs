@app.route("/")
def index():
    return '''
    <script>
    if (top !== self) {
        top.location = self.location;
    }
    </script>
    vulnerable page
    '''
