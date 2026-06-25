// Copied from http://github.com/sstephenson/prototype/blob/c480bd7b97f6c7ca2d49f8649320436eea7f0aed/src/lang/class.js

Object.prototype.extend = function(source) {
  for (var property in source)
    this[property] = source[property];
  return this;
}

Object.prototype.extend({
  toArray: function() {
    var result = [];
    for( var i = 0; i < this.length; i++ )
      result[i] = this[i];
    return result;
  },
  
  keys: function() {
    var result = [];
    for( var key in this )
      result.push(key);
    return result;
  },
  
  each: function( block ) {
    for( var key in this ) {
      if( this.constructor.prototype[key] || Object.prototype[key] )
        continue;
      block( key, this[key] );
    }
  },
  
  toString_: function() {
    var result = "{ ";
    for( var key in this ) {
      var value = this[key];
      if( !(value instanceof Function) ) {
        value = ( value == undefined ) ? 'undefined' : value.toString();
        result = result + key + ':' + ' ' + value + ', ';
      }
    }
    return result + ' }';
  }
});

/* Based on Alex Arnell's inheritance implementation. */
 
var Class = (function() {
  /**
* Class.create([superclass][, methods...]) -> Class
* - superclass (Class): The optional superclass to inherit methods from.
* - methods (Object): An object whose properties will be "mixed-in" to the
* new class. Any number of mixins can be added; later mixins take
* precedence.
*
* Creates a class.
*
* Class.create returns a function that, when called, will fire its own
* `initialize` method.
*
* `Class.create` accepts two kinds of arguments. If the first argument is
* a `Class`, it's treated as the new class's superclass, and all its
* methods are inherited. Otherwise, any arguments passed are treated as
* objects, and their methods are copied over as instance methods of the new
* class. Later arguments take precedence over earlier arguments.
*
* To extend a class after it has been defined, use [[Class#addMethods]].
**/
  function create() {
    var parent = null;
    var properties = arguments.toArray();
    if( properties[0] instanceof Function )
      parent = properties.shift();
          
    function klass() {
      this.initialize.apply(this, arguments);
    }
    
    klass.extend( Class.Methods );
    klass.superclass = parent;
    klass.subclasses = [];
    
    if (parent) {
      var subclass = function() {};
      subclass.prototype = parent.prototype;
      subclass.constructor = klass;
      klass.prototype = new subclass;
      parent.subclasses.push(klass);
    }
    
    for (var i = 0; i < properties.length; i++)
      klass.addMethods(properties[i]);
      
    if (!klass.prototype.initialize)
      klass.prototype.initialize = function () {};
    
    klass.prototype.constructor = klass;
    return klass;
  }
  
  /**
* Class#addMethods(methods) -> Class
* - methods (Object): The methods to add to the class.
*
* Adds methods to an existing class.
*
* `Class#addMethods` is a method available on classes that have been
* defined with `Class.create`. It can be used to add new instance methods
* to that class, or overwrite existing methods, after the class has been
* defined.
*
* New methods propagate down the inheritance chain. If the class has
* subclasses, those subclasses will receive the new methods — even in the
* context of `$super` calls. The new methods also propagate to instances of
* the class and of all its subclasses, even those that have already been
* instantiated.
**/
  function addMethods(source) {
    var ancestor = this.superclass && this.superclass.prototype;
    var properties = source.keys();
    
    // IE6 doesn't enumerate toString and valueOf properties,
    // Force copy if they're not coming from Object.prototype.
    if (!{ toString: true }.keys().length) {
      if (source.toString != Object.prototype.toString)
        properties.push("toString");
      if (source.valueOf != Object.prototype.valueOf)
        properties.push("valueOf");
    }

    for (var i = 0, length = properties.length; i < length; i++) {
      var property = properties[i];
      this.prototype[property] = source[property];
    }
    
    return this;
  }
  
  function classApply( name ) {
    var klass = this;
    var properties = arguments.toArray();
    properties.shift();
    
    while( klass ) {
      if( klass[name] )
        return klass[name].apply( this, properties );
      klass = klass.superclass;
    }
  }

  function classCall( name ) {
    var properties = arguments.toArray();
    properties.shift();  
    return this.classApply( name, properties );
  }

  return {
    create: create,
    Methods: {
      addMethods: addMethods,
      classApply: classApply,
      classCall: classCall
    }
  };
})();