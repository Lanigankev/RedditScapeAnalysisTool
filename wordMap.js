function wordMap(){
	//find words in the document text
    var summary = this.body;
    if (summary) { 
        //summary = summary.replace(/[.,!@#$%^&*?:;{}()[]]/g, "")
        // quick lowercase to normalize per your requirements
        summary = summary.toLowerCase().split(" "); 
        for (var i = summary.length; i >= 0; i--) {
            // might want to remove punctuation, etc. here
            if (summary[i]&&summary[i].length<45)  {
         // make sure there's something
               emit(summary[i], 1); // store a 1 for each word
                
            }
        }
    }
}