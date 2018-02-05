package firstOne;

public class HelloWorld {
    public String ex, avf;
    public int test;
    public HelloWorld self;

    public HelloWorld(int test){
        this.test = test;
    }

    public static void main(String[] args, SomeClassName c) {

        String f = 'Hello!!!';
        String a = c;
        HelloWorld d = new HelloWorld(a);
        c = "new value";
        d = new HelloWorld(434);
        d.self.get().test = 5;
        d.get().test.vtest = 4;
        d.print(a);
        d.create(a);
        //return 2+4;
    }

    private void print(String a){
        // something happened
        int f = 43;
        // int d = a.b.create_fail();
        int d1 = this.create();
        int sd = this;
        this.test = 0;
    }

    private void create(String a){
        // something happened
        int f = 43;
        int d1 = f*2+2;
        1 + 2 + 3;
    }

    private void get(){
        return this;
    }
}

//({'a', 'args', 'b', 'c'}, {'d', 'f', 'fg'})
