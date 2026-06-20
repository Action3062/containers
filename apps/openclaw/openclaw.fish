function openclaw --description 'Wrapper around the OpenClaw CLI baked into the image'
    command node /app/dist/index.js $argv
end
