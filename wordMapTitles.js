function wordMap(){
	//find words in the document text
    var summary = this.title;
    if (summary) { 
        summary = summary.toLowerCase().split(" "); 
        for (var i = summary.length; i >= 0; i--) {
            //make sure there is a value to be emitted
            // and that the word does not exceed 45 characters
            if (summary[i]&&summary[i].length<45)  {
         
               emit(summary[i], 1); 
                
            }
        }
    }
}