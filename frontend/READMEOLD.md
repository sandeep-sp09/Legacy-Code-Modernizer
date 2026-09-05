# Frontend / UI

Displays:
1. File upload for Pascal/C source.
2. Dependency graph visualization.
3. Side-by-side diff view (original source vs. generated C++).

## Suggested stack
Streamlit (fastest to build for a college project) OR React (if more control over
diff/graph rendering is needed).

## TODO
- [ ] File upload component
- [ ] Call backend /upload and /process endpoints
- [ ] Render dependency graph (from JSON returned by backend)
- [ ] Render side-by-side code diff view
- [ ] Basic styling / layout
