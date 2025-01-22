const fs = require('fs');
const tar = require('tar-stream');
const zlib = require('zlib');
const crypto = require('crypto');

// const getCurrentFiles = () => {
//     fs.readdir(__dirname, (err, files) => {
//         if (err){
//             console.error('Error reading the directory:', err);
//             return;
//         };

//         console.log('Files in the current directory:');

//         files.forEach(file => {
//             console.log(file);
//         });
//     })
// };

// const generateFileId = fileName => {
//     return crypto.createHash('md5').update(fileName + Date.now()).digest('hex');
// }

// define tar-stream extract object

const extract = tar.extract();

extract.on('entry', (header, stream, next) => {

    if (header.type === "directory"){
        stream.resume()
        next();
    } else if (header.type === "file"){
        console.log(`header name: ${header.name}`);
        stream.resume()
        stream.on('end', next); // Proceed to the next entry after writing
    }
});

extract.on('error', err => {
    console.log(`Error: ${err}`);
})


extract.on('finish', () => {
    console.log('Extraction complete.');
})

// Read the tar file and pipe it into the extractor
tarFilePath = '/home/chunwei/src/test.tar.gz';
fs.createReadStream(tarFilePath).pipe(zlib.createGunzip()).pipe(extract)