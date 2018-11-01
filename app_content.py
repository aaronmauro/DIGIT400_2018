# CMS Structure: Title, Path, Message
def content():
    APP_CONTENT = {
        "Home":[["Welcome","/welcome/","Welcome to my app, you can do many things here!"],
                ["Background","/background/","We had a lot of fun building this app. Learn more about our story."],
                ["Messages","/messages/","Get your messages from the community!"],],
        
        "User_Files":[["Static Download","/download/","Download a single static file!"],
                ["Photo Upload","/uploads/","Upload your user photos here."],
                ["Download Files","/downloader/","Download files by file name here. Try to improve me by linking in the database!"],],
        
        "Contact":[["Contact Us","/contact/","Get in touch! We'd love to hear from you!"],],
    }
    return APP_CONTENT