const fs = require('fs');
let crndata, titles;

fs.readFile('crnlist.json', 'utf8', (err, data) => {
    if (!err) crndata = JSON.parse(data);
});
  
fs.readFile('crntotitle.json', 'utf8', (err, data) => {
    if (!err) titles = JSON.parse(data);
});

let flag = true;
while(flag) {
    let CRN = prompt("Enter CRN: ");
    let dataDict = crndata[CRN][0];
    let title = titles[CRN];

    console.log("Course Title: " + title);
}