Plainsight, a textual steganography tool to defeat censorship.
==============================================================

Contact
-------
* Author: Robert Winslow
* Source: http://github.com/rw/plainsight
* Email: robert.winslow@gmail.com


Description
-----------
The goal of Plainsight is to help you avoid being flagged as 'suspicious' by
internet censors. By using Plainsight, your data will be enciphered to look
like harmless English prose. When you transmit it to someone else, eaves-
droppers will only see the written word, and not your data payload.

This is an improvement over just sending an encrypted file, because no
suspicious random-looking bitstreams are seen by others.


How to use
----------

1. Install it:

    sudo pip install plainsight

2. Download a copy of 'The Adventures of Sherlock Holmes'

    curl -o sherlock.txt http://www.gutenberg.org/cache/epub/1661/pg1661.txt

3. Type your message to encode:

    echo 'Meet at Union Square at noon. The password is FuriousGreen.' > cleartext

4. Then, pipe it through Plainsight:

    cat cleartext | plainsight -m encipher -f sherlock.txt > ciphertext

5. The output will be gibberish that Doyle could've written:

      cat ciphertext |fold -s
      which was the case, of a light. And, his hand. "BALLARAT." only applicant?" 
      decline be walking we do, the point of the little man in a strange, her 
      husband's hand, going said road, path but you do know what I have heard of you, 
      I found myself to get away from home and for the ventilator little cold night, 
      and I he had left my friend Sherlock of our visitor and he had an idea was not 
      to abuse step I of you, I knew what I was then the first signs it is the 
      daughter, at least a fellow-countryman. had come. as I have already explained, 
      the garden. what you can see a of importance. your hair. a picture upon of the 
      money which had brought a you have a little good deal in way: out to my wife 
      and hurry." made your hair. a charge me a series events, and excuse no sign his 
      note-book has come away and in my old Sherlock was already down to do with the 
      twisted

6. Now, decipher that ciphertext:

    cat ciphertext | plainsight -m decipher -f sherlock.txt > deciphered
    cat deciphered
    Meet at Union Square at noon. The password is FuriousGreen.


TODO
----
* Fuzz testing.
* More entropic ciphertexts.
*   (e.g. play with changing the probability mass as tree depth increases).
* Regression tests (e.g. for EOF).
* Robust adding of files to language model (e.g. independent of args order).
* Model serialization to pickled Python objects.
* Higher throughput.
* Tighter code.
* Support for other languages (e.g. Chinese).
* Port to other languages (e.g. Ruby).


Bugs
----
The last few bits of a file can be garbled when deciphered.
  Workaround: check that the deciphered output matches the original cleartext.


License
-------

Copyright (c) 2011, Robert Winslow
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

The names of the contributors may not be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
