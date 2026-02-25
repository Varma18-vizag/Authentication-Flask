Hello Everyone, This is My Flask code for the Authentication using  user register , login , otp sending to email , otp verification , change the password 

Here  I have used Supabase Cloud  for Database Management

Real usage diagram of the apis in the frontend ::-->>


     
             user register 
                    | (body : name , username , email , password)
                   \ /
             user login 
                    |  (body : username , password)  (response message -> jwt token)
                   \ /     



-> password change 
       |
      \ /
    1. user existsing (registration check) 
             |  (body : username , email)  (response : username , email)
            \ /
    2. api create -> send through email -> storing the encrypted otp in the database 
             |  (body : username , email)  (response : username , email)
            \ / 
        ------------------------------------------------------------------                
        | (after timeout)                                                |
       \ /                                                              \ /
       2a . delete the user otp using the username , email                2b. otp verification ()
                                                                               |  body : (otp , username , email) , response : (isVerified ,      username , email)
                                                                              \ /
                                                                            allow access to the user to chage the password#
