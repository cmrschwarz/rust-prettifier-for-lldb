# rust-prettifier-for-lldb, Christian Schwarz, 2024

# This file is based on by vadimcn/codelldb by Vadim Chugunov
# https://github.com/vadimcn/codelldb/blob/05502bf75e4e7878a99b0bf0a7a81bba2922cbe3/formatters/rust.py
# The original version was used and adapted under the terms of the MIT License:
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Vadim Chugunov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from __future__ import print_function, division
import sys
import lldb  # type: ignore
import weakref
import re

module = sys.modules[__name__]
rust_category = None
lldb_major_version = None

MAX_STRING_SUMMARY_LENGTH = 1024
MAX_SEQUENCE_SUMMARY_LENGTH = 10

TARGET_ADDR_SIZE = 8


def initialize_category(debugger, internal_dict):
    global rust_category, MAX_STRING_SUMMARY_LENGTH, TARGET_ADDR_SIZE, lldb_major_version

    version_string_match = re.match(
        r"lldb version (\d+)\.\d+",
        lldb.SBDebugger.GetVersionString(),
        re.IGNORECASE
    )
    if version_string_match is not None:
        lldb_major_version = version_string_match.groups(1)

    # remove previous conflicting prettifiers potentially added e.g. by CodeLLDB
    rust_category = debugger.DeleteCategory('Rust')
    rust_category = debugger.CreateCategory('Rust')
    # rust_category.AddLanguage(lldb.eLanguageTypeRust)
    rust_category.SetEnabled(True)

    attach_synthetic_to_type(TupleSynthProvider, r'^\(.*\)$', True)
    # *-windows-msvc uses this name since 1.47
    attach_synthetic_to_type(MsvcTupleSynthProvider, r'^tuple\$?<.+>$', True)

    attach_synthetic_to_type(CharSynthProvider, 'char32_t')

    # there is no 1 byte char type in rust, so these have to be u8/i8
    attach_synthetic_to_type(U8SynthProvider, 'unsigned char')
    attach_synthetic_to_type(I8SynthProvider, 'char')

    attach_synthetic_to_type(StrSliceSynthProvider, '&str')
    attach_synthetic_to_type(StrSliceSynthProvider, 'str*')
    # *-windows-msvc uses this name since 1.5?
    attach_synthetic_to_type(StrSliceSynthProvider, 'str')
    attach_synthetic_to_type(StrSliceSynthProvider, 'ref$<str$>')
    attach_synthetic_to_type(StrSliceSynthProvider, 'ref_mut$<str$>')

    attach_synthetic_to_type(StdStringSynthProvider,
                             '^(collections|alloc)::string::String$', True)
    attach_synthetic_to_type(StdVectorSynthProvider,
                             r'^(collections|alloc)::vec::Vec<.+>$', True)
    attach_synthetic_to_type(StdVecDequeSynthProvider,
                             r'^(collections|alloc::collections)::vec_deque::VecDeque<.+>$', True)

    attach_synthetic_to_type(MsvcEnumSynthProvider, r'^enum\$<.+>$', True)
    attach_synthetic_to_type(MsvcEnum2SynthProvider, r'^enum2\$<.+>$', True)

    attach_synthetic_to_type(SliceSynthProvider, r'^&(mut *)?\[.*\]$', True)
    attach_synthetic_to_type(MsvcSliceSynthProvider,
                             r'^(mut *)?slice\$?<.+>.*$', True)
    attach_synthetic_to_type(MsvcSliceSynthProvider,
                             r'^ref(_mut)?\$<slice2\$<.+>.*>$', True)

    attach_synthetic_to_type(StdCStringSynthProvider,
                             '^(std|alloc)::ffi::c_str::CString$', True)
    attach_synthetic_to_type(StdCStrSynthProvider,
                             '^&?(std|core)::ffi::c_str::CStr$', True)
    attach_synthetic_to_type(StdCStrSynthProvider,
                             'ref$<core::ffi::c_str::CStr>')
    attach_synthetic_to_type(StdCStrSynthProvider,
                             'ref_mut$<core::ffi::c_str::CStr>')

    attach_synthetic_to_type(StdOsStringSynthProvider,
                             'std::ffi::os_str::OsString')
    attach_synthetic_to_type(StdOsStrSynthProvider,
                             '^&?std::ffi::os_str::OsStr', True)
    attach_synthetic_to_type(StdOsStrSynthProvider,
                             'ref$<std::ffi::os_str::OsStr>')
    attach_synthetic_to_type(StdOsStrSynthProvider,
                             'ref_mut$<std::ffi::os_str::OsStr>')

    attach_synthetic_to_type(StdPathBufSynthProvider, 'std::path::PathBuf')
    attach_synthetic_to_type(StdPathSynthProvider, '^&?std::path::Path', True)
    attach_synthetic_to_type(StdPathSynthProvider, 'ref$<std::path::Path>')
    attach_synthetic_to_type(StdPathSynthProvider, 'ref_mut$<std::path::Path>')

    attach_synthetic_to_type(StdRcSynthProvider, r'^alloc::rc::Rc<.+>$', True)
    attach_synthetic_to_type(
        StdRcSynthProvider, r'^alloc::rc::Weak<.+>$', True)
    attach_synthetic_to_type(
        StdArcSynthProvider, r'^alloc::(sync|arc)::Arc<.+>$', True)
    attach_synthetic_to_type(
        StdArcSynthProvider, r'^alloc::(sync|arc)::Weak<.+>$', True)
    attach_synthetic_to_type(StdMutexSynthProvider,
                             r'^std::sync::mutex::Mutex<.+>$', True)

    attach_synthetic_to_type(StdCellSynthProvider,
                             r'^core::cell::Cell<.+>$', True)
    attach_synthetic_to_type(StdUnsafeCellSynthProvider,
                             r'^core::cell::UnsafeCell<.+>$', True)
    attach_synthetic_to_type(StdRefCellSynthProvider,
                             r'^core::cell::RefCell<.+>$', True)
    attach_synthetic_to_type(
        StdRefCellBorrowSynthProvider, r'^core::cell::Ref<.+>$', True)
    attach_synthetic_to_type(
        StdRefCellBorrowSynthProvider, r'^core::cell::RefMut<.+>$', True)

    attach_synthetic_to_type(
        StdHashMapSynthProvider, r'^std::collections::hash::map::HashMap<.+>$', True)
    attach_synthetic_to_type(
        StdHashSetSynthProvider, r'^std::collections::hash::set::HashSet<.+>$', True)

    attach_synthetic_to_type(OptionSynthProvider,
                             r'^core::option::Option<.+>$', True)
    attach_synthetic_to_type(ResultSynthProvider,
                             r'^core::result::Result<.+>$', True)
    attach_synthetic_to_type(CowSynthProvider,
                             r'^alloc::borrow::Cow<.+>$', True)

    attach_synthetic_to_type(CrossbeamAtomicCellSynthProvider,
                             r'^crossbeam_utils::atomic::atomic_cell::AtomicCell<.+>$', True)

    debugger.HandleCommand(
        "type summary add"
        + f" --python-function {__name__}.enum_summary_provider"
        + f" --recognizer-function {__name__}.enum_recognizer_function",
    )
    debugger.HandleCommand(
        "type synthetic add"
        + f" --python-class {__name__}.GenericEnumSynthProvider"
        + f" --recognizer-function {__name__}.enum_recognizer_function",
    )

    if 'rust' in internal_dict.get('source_languages', []):
        lldb.SBDebugger.SetInternalVariable('target.process.thread.step-avoid-regexp',
                                            '^<?(std|core|alloc)::', debugger.GetInstanceName())

    # The GetSetting method is not available on older LLDB versions
    try:
        MAX_STRING_SUMMARY_LENGTH = debugger.GetSetting(
            'target.max-string-summary-length').GetIntegerValue()
    except:
        pass

    try:
        TARGET_ADDR_SIZE = debugger.GetSelectedTarget().addr_size
    except:
        pass


def attach_synthetic_to_type(synth_class, type_name, is_regex=False):
    global module, rust_category
    synth = lldb.SBTypeSynthetic.CreateWithClassName(
        __name__ + '.' + synth_class.__name__)
    synth.SetOptions(lldb.eTypeOptionCascade)
    rust_category.AddTypeSynthetic(
        lldb.SBTypeNameSpecifier(type_name, is_regex), synth)

    def summary_fn(valobj, dict):
        return get_synth_summary(synth_class, valobj, dict)

    # LLDB accesses summary fn's by name, so we need to create a unique one.
    summary_fn.__name__ = '_get_synth_summary_' + synth_class.__name__
    setattr(module, summary_fn.__name__, summary_fn)
    attach_summary_to_type(summary_fn, type_name, is_regex)


def attach_summary_to_type(summary_fn, type_name, is_regex=False):
    global module, rust_category
    summary = lldb.SBTypeSummary.CreateWithFunctionName(
        __name__ + '.' + summary_fn.__name__
    )
    summary.SetOptions(lldb.eTypeOptionCascade)
    rust_category.AddTypeSummary(
        lldb.SBTypeNameSpecifier(type_name, is_regex), summary
    )


# 'get_summary' is annoyingly not a part of the standard LLDB synth provider API.
# This trick allows us to share data extraction logic between synth providers and their sibling summary providers.
def get_synth_summary(synth_class, valobj, dict):
    obj_id = valobj.GetIndexOfChildWithName('$$object-id$$')
    summary = RustSynthProvider.synth_by_id[obj_id].get_summary()

    if summary is None:
        raise Exception("Could not provide summary for given object")
    else:
        return str(summary)


# Chained GetChildMemberWithName lookups
def gcm(valobj, *chain):
    for name in chain:
        valobj = valobj.GetChildMemberWithName(name)
    return valobj


# Get a pointer out of core::ptr::Unique<T>
def read_unique_ptr(valobj):
    pointer = valobj.GetChildMemberWithName('pointer')
    if pointer.TypeIsPointerType():  # Between 1.33 and 1.63 pointer was just *const T
        return pointer
    return pointer.GetChildAtIndex(0)


def string_from_addr(process, addr, length):
    if length <= 0:
        return u''
    error = lldb.SBError()
    data = process.ReadMemory(addr, length, error)
    if error.Success():
        return data.decode('utf8', 'replace')
    else:
        raise Exception('ReadMemory error: %s', error.GetCString())


def string_from_ptr(pointer, length):
    return string_from_addr(pointer.GetProcess(), pointer.GetValueAsUnsigned(), length)


# turns foo::Bar::Baz<T>::Quux<Q> into Quux<Q>
def unscope_typename(type_name):
    start = 0
    level = 0
    prev_was_quote = False
    for i, c in enumerate(type_name):
        if c == '<':
            level += 1
            continue
        if c == '>':
            level -= 1
            continue
        if c == ':':
            if prev_was_quote:
                if level == 0:
                    start = i + 1
                prev_was_quote = False
                continue
            prev_was_quote = True
            continue
        prev_was_quote = False

    return type_name[start::]

# turns Cow<str>::Borrowed::<str>("asdf") into Cow::Borrowed("asdf")
def drop_template_args(type_name):
    res = ""
    level = 0
    start = 0
    for i, c in enumerate(type_name):
        if c == '<':
            if level == 0:
                res += type_name[start:i]
            level += 1
        elif c == '>':
            level -= 1
            if level == 0:
                start = i + 1
    res += type_name[start:]
    return res


def get_template_params(type_name):
    params = []
    level = 0
    start = 0
    for i, c in enumerate(type_name):
        if c == '<':
            level += 1
            if level == 1:
                start = i + 1
        elif c == '>':
            level -= 1
            if level == 0:
                params.append(type_name[start:i].strip())
        elif c == ',' and level == 1:
            params.append(type_name[start:i].strip())
            start = i + 1
    return params


def obj_summary(valobj, obj_typename=None, unavailable='{...}', parenthesize_single_value=False, max_len=32):
    summary = valobj.GetSummary()
    if summary is not None:
        if parenthesize_single_value:
            return f"({summary})"
        return summary
    child_count = valobj.GetNumChildren()
    if child_count != 0:
        if valobj.GetChildAtIndex(0).GetName() in ['0', '__0'] and obj_typename is None:
            return tuple_summary(valobj)

        if obj_typename is None:
            summary = "{"
        else:
            summary = f"{obj_typename}{{"

        for i in range(child_count):
            name = valobj.GetType().GetFieldAtIndex(i).GetName()
            value = valobj.GetChildAtIndex(i)
            member_summary = f"{name}: {obj_summary(value)}"
            if i != 0:
                summary += ", "
            if len(summary) + 1 + len(member_summary) > max_len:
                summary += ".."
                break
            summary += member_summary
        summary += "}"
        if obj_typename is not None and parenthesize_single_value:
            return f"({summary})"
        return summary

    summary = valobj.GetValue()
    if summary is not None:
        if obj_typename is None:
            res = summary
        else:
            res = f"{obj_typename}({summary})"
        if parenthesize_single_value:
            return f"({res})"
        return res

    return unavailable


def sequence_summary(childern, max_len=MAX_STRING_SUMMARY_LENGTH, max_elem_count= MAX_SEQUENCE_SUMMARY_LENGTH):
    s = ''
    for (i, child) in enumerate(childern):
        if len(s) > 0:
            s += ', '
        summary = obj_summary(child)
        if len(s + summary) > max_len or i >= max_elem_count:
            s += '...'
            break
        s += summary
    return s


def tuple_summary(obj, skip_first=0, max_len=32, include_parens=True):
    if include_parens:
        s = "("
    else:
        s = ""
    for i in range(skip_first, obj.GetNumChildren()):
        if i > 0:
            s += ', '
        os = obj_summary(obj.GetChildAtIndex(i), max_len=max_len-len(s)-1)
        if len(s) + len(os) + int(include_parens) > max_len:
            s += '..'
            break
        s += os
    if include_parens:
        s += ')'
    return s


class RustSynthProvider(object):
    synth_by_id = weakref.WeakValueDictionary()
    next_id = 0
    obj_id = 0
    valobj = None
    summary = None

    def __init__(self, valobj, dict={}):
        self.valobj = valobj
        self.obj_id = RustSynthProvider.next_id
        RustSynthProvider.synth_by_id[self.obj_id] = self
        RustSynthProvider.next_id += 1

    def update(self):
        return True

    def has_children(self):
        return False

    def num_children(self):
        return 0

    def get_child_at_index(self, index):
        return None

    def get_child_index(self, name):
        if name == '$$object-id$$':
            return self.obj_id

        return self.get_index_of_child(name)

    def get_summary(self):
        return self.summary


class CharSynthProvider(RustSynthProvider):
    def update(self):
        value = self.valobj.GetValueAsUnsigned()
        c = chr(value)
        if c.isprintable():
            self.summary = f"'{c}'"
        else:
            self.summary = f"U+0x{value:08X}"


class U8SynthProvider(RustSynthProvider):
    def update(self):
        value = self.valobj.GetValueAsUnsigned()
        self.summary = f"{int(value)}"


class I8SynthProvider(RustSynthProvider):
    def update(self):
        value = self.valobj.GetValueAsSigned()
        self.summary = f"{int(value)}"


class TupleSynthProvider(RustSynthProvider):
    def update(self):
        self.summary = tuple_summary(self.valobj)

    def has_children(self):
        return True

    def num_children(self):
        return self.valobj.GetNumChildren()

    def get_index_of_child(self, name):
        return int(name.lstrip('_[').rstrip(']'))

    def get_child_at_index(self, index):
        value = self.valobj.GetChildAtIndex(index)
        value = self.valobj.CreateValueFromData(str(index), value.GetData(), value.GetType())
        return value


class ArrayLikeSynthProvider(RustSynthProvider):
    '''Base class for providers that represent array-like objects'''

    def update(self):
        self.ptr, self.len = self.ptr_and_len(self.valobj)  # type: ignore
        self.item_type = self.ptr.GetType().GetPointeeType()
        self.item_size = self.item_type.GetByteSize()

    def ptr_and_len(self, obj):
        pass  # abstract

    def num_children(self):
        return self.len

    def has_children(self):
        return True

    def get_child_at_index(self, index):
        if not 0 <= index < self.len:
            return None
        offset = index * self.item_size
        return self.ptr.CreateChildAtOffset('[%s]' % index, offset, self.item_type)

    def get_index_of_child(self, name):
        return int(name.lstrip('[').rstrip(']'))

    def get_summary(self):
        return '(%d)' % (self.len,)


class StdVectorSynthProvider(ArrayLikeSynthProvider):
    def ptr_and_len(self, vec):
        element_type = self.valobj.GetType().GetTemplateArgumentType(0)
        ptr = read_unique_ptr(gcm(vec, 'buf', 'inner', 'ptr', 'pointer'))
        ptr = ptr.Cast(element_type.GetPointerType())
        len = gcm(vec, 'len').GetValueAsUnsigned()
        return (ptr, len)

    def get_summary(self):
        return '(%d) vec![%s]' % (self.len, sequence_summary((self.get_child_at_index(i) for i in range(self.len))))


class StdVecDequeSynthProvider(RustSynthProvider):
    def update(self):
        element_type = self.valobj.GetType().GetTemplateArgumentType(0)
        ptr = read_unique_ptr(
            gcm(self.valobj, 'buf', 'inner', 'ptr', 'pointer'))
        self.ptr = ptr.Cast(element_type.GetPointerType())
        self.cap = (
            gcm(self.valobj, 'buf', 'inner', 'cap')
            .GetChildAtIndex(0)
            .GetValueAsUnsigned()
        )

        head = gcm(self.valobj, 'head').GetValueAsUnsigned()

        # rust 1.67 changed from a head, tail implementation to a head, length impl
        # https://github.com/rust-lang/rust/pull/102991
        vd_len = gcm(self.valobj, 'len')
        if vd_len.IsValid():
            self.len = vd_len.GetValueAsUnsigned()
            self.startptr = head
        else:
            tail = gcm(self.valobj, 'tail').GetValueAsUnsigned()
            self.len = head - tail
            self.startptr = tail

        self.item_type = self.ptr.GetType().GetPointeeType()
        self.item_size = self.item_type.GetByteSize()

    def num_children(self):
        return self.len

    def has_children(self):
        return True

    def get_child_at_index(self, index):
        if not 0 <= index < self.num_children():
            return None
        offset = ((self.startptr + index) % self.cap) * self.item_size
        return self.ptr.CreateChildAtOffset('[%s]' % index, offset, self.item_type)

    def get_index_of_child(self, name):
        return int(name.lstrip('[').rstrip(']'))

    def get_summary(self):
        return '(%d) VecDeque[%s]' % (
            self.num_children(),
            sequence_summary((self.get_child_at_index(i)
                             for i in range(self.num_children())))
        )


class SliceSynthProvider(ArrayLikeSynthProvider):
    def ptr_and_len(self, vec):
        return (
            gcm(vec, 'data_ptr'),
            gcm(vec, 'length').GetValueAsUnsigned()
        )

    def get_summary(self):
        return '(%d) &[%s]' % (self.len, sequence_summary((self.get_child_at_index(i) for i in range(self.len))))


class MsvcSliceSynthProvider(SliceSynthProvider):
    def get_type_name(self):
        tparams = get_template_params(self.valobj.GetTypeName())
        return '&[' + tparams[0] + ']'


# Base class for *String providers
class StringLikeSynthProvider(ArrayLikeSynthProvider):
    def update(self):
        super().update()
        self.strval = string_from_ptr(
            self.ptr,
            min(self.len, MAX_STRING_SUMMARY_LENGTH)
        )
        if self.len > MAX_STRING_SUMMARY_LENGTH:
            self.strval += u'...'

    def get_child_at_index(self, index):
        ch = ArrayLikeSynthProvider.get_child_at_index(self, index)
        ch.SetFormat(lldb.eFormatChar)
        return ch

    def get_summary(self):
        return u'"%s"' % self.strval


class StrSliceSynthProvider(StringLikeSynthProvider):
    def ptr_and_len(self, valobj):
        return (
            gcm(valobj, 'data_ptr'),
            gcm(valobj, 'length').GetValueAsUnsigned()
        )

    def get_type_name(self):
        return '&str'


class StdStringSynthProvider(StringLikeSynthProvider):
    def ptr_and_len(self, valobj):
        vec = gcm(valobj, 'vec')
        return (
            read_unique_ptr(gcm(vec, 'buf', 'inner', 'ptr', 'pointer')),
            gcm(vec, 'len').GetValueAsUnsigned()
        )


class StdCStringSynthProvider(StringLikeSynthProvider):
    def ptr_and_len(self, valobj):
        vec = gcm(valobj, 'inner')
        return (
            gcm(vec, 'data_ptr'),
            gcm(vec, 'length').GetValueAsUnsigned() - 1
        )


class StdOsStringSynthProvider(StringLikeSynthProvider):
    def ptr_and_len(self, valobj):
        vec = gcm(valobj, 'inner', 'inner')
        tmp = gcm(vec, 'bytes')  # Windows OSString has an extra layer
        if tmp.IsValid():
            vec = tmp
        return (
            read_unique_ptr(gcm(vec, 'buf', 'ptr')),
            gcm(vec, 'len').GetValueAsUnsigned()
        )


class FFISliceSynthProvider(StringLikeSynthProvider):
    def ptr_and_len(self, valobj):
        process = valobj.GetProcess()
        slice_ptr = valobj.GetLoadAddress()
        data_ptr_type = valobj.GetTarget().GetBasicType(
            lldb.eBasicTypeChar).GetPointerType()
        # Unsized slice objects have incomplete debug info, so here we just assume standard slice
        # reference layout: [<pointer to data>, <data size>]
        error = lldb.SBError()
        pointer = valobj.CreateValueFromAddress(
            'data', slice_ptr, data_ptr_type)
        length = process.ReadPointerFromMemory(
            slice_ptr + process.GetAddressByteSize(), error)
        return pointer, length


class StdCStrSynthProvider(FFISliceSynthProvider):
    def ptr_and_len(self, valobj):
        ptr, len = FFISliceSynthProvider.ptr_and_len(self, valobj)
        return (ptr, len-1)  # drop terminaing '\0'


class StdOsStrSynthProvider(FFISliceSynthProvider):
    pass


class StdPathBufSynthProvider(StdOsStringSynthProvider):
    def ptr_and_len(self, valobj):
        return StdOsStringSynthProvider.ptr_and_len(self, gcm(valobj, 'inner'))


class StdPathSynthProvider(FFISliceSynthProvider):
    pass


class DerefSynthProvider(RustSynthProvider):
    deref = lldb.SBValue()

    def has_children(self):
        return self.deref.MightHaveChildren()

    def num_children(self):
        return self.deref.GetNumChildren()

    def get_child_at_index(self, index):
        return self.deref.GetChildAtIndex(index)

    def get_index_of_child(self, name):
        return self.deref.GetIndexOfChildWithName(name)

    def get_summary(self):
        return obj_summary(self.deref)


# Base for Rc and Arc
class StdRefCountedSynthProvider(RustSynthProvider):
    weak = 0
    strong = 0
    slice_len = None
    value = None

    def has_children(self):
        return True

    def num_children(self):
        return self.value.GetNumChildren() if self.slice_len is None else self.slice_len

    def get_child_at_index(self, i):
        if self.slice_len:
            elem_size = self.value.GetByteSize()
            return self.value.CreateChildAtOffset(
                f'[{i}]', i * elem_size, self.value.GetType()
            )

        return self.value.GetChildAtIndex(i)


    def get_index_of_child(self, name):
        if self.slice_len is not None:
            return int(name.lstrip('[').rstrip(']'))

        return self.value.GetIndexOfChildWithName(name)

    def get_summary(self):
        if self.weak != 0:
            s = '(strong:%d, weak:%d) ' % (self.strong, self.weak)
        else:
            s = '(strong:%d) ' % self.strong
        if self.strong > 0:
            if self.slice_len is not None:
                if self.value.GetType().GetName() == "unsigned char":
                    str_data = string_from_addr(
                        self.value.GetProcess(),
                        self.value.GetLoadAddress(),
                        min(MAX_STRING_SUMMARY_LENGTH, self.slice_len)
                    )
                    s += f"\"{str_data}\""
                else:
                    s += "[%s]" % sequence_summary((
                        self.get_child_at_index(i) for i in range(self.slice_len)
                    ))
            else:
                s += obj_summary(self.value)
        else:
            s += '<disposed>'
        return s


class StdRcSynthProvider(StdRefCountedSynthProvider):
    def update(self):
        inner = read_unique_ptr(gcm(self.valobj, 'ptr'))
        self.strong = gcm(inner, 'strong', 'value', 'value').GetValueAsUnsigned()
        self.weak = gcm(inner, 'weak', 'value', 'value').GetValueAsUnsigned()
        if self.strong > 0:
            self.value = gcm(inner, 'value')
            self.weak -= 1  # There's an implicit weak reference communally owned by all the strong pointers
            if self.valobj.GetType().size == 2 * TARGET_ADDR_SIZE:
                self.slice_len = gcm(self.valobj, "ptr", "pointer", "length").GetValueAsUnsigned()
        else:
            self.value = lldb.SBValue()
        self.value.SetPreferSyntheticValue(True)


class StdArcSynthProvider(StdRefCountedSynthProvider):
    def update(self):
        inner = read_unique_ptr(gcm(self.valobj, 'ptr'))
        self.strong = gcm(inner, 'strong', 'v', 'value').GetValueAsUnsigned()
        self.weak = gcm(inner, 'weak', 'v', 'value').GetValueAsUnsigned()
        if self.strong > 0:
            self.value = gcm(inner, 'data')
            if self.valobj.GetType().size == 2 * TARGET_ADDR_SIZE:
                self.slice_len = gcm(self.valobj, "ptr", "pointer", "length").GetValueAsUnsigned()
            self.weak -= 1  # There's an implicit weak reference communally owned by all the strong pointers
        else:
            self.value = lldb.SBValue()
        self.value.SetPreferSyntheticValue(True)


class StdMutexSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'data', 'value')
        self.deref.SetPreferSyntheticValue(True)


class StdCellSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'value', 'value')
        self.deref.SetPreferSyntheticValue(True)


class StdUnsafeCellSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'value')
        self.deref.SetPreferSyntheticValue(True)

class StdRefCellSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'value', 'value')
        self.deref.SetPreferSyntheticValue(True)

    def get_summary(self):
        borrow = gcm(self.valobj, 'borrow', 'value',
                     'value').GetValueAsSigned()
        s = ''
        if borrow < 0:
            s = '(borrowed:mut) '
        elif borrow > 0:
            s = '(borrowed:%d) ' % borrow
        return s + obj_summary(self.deref)


class StdRefCellBorrowSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'value', 'pointer').Dereference()
        self.deref.SetPreferSyntheticValue(True)


class EnumSynthProvider(RustSynthProvider):
    variant = lldb.SBValue()
    typename_summary = ""
    variant_name = ""
    variant_summary = ""
    skip_first = 0

    def has_children(self):
        return self.variant.MightHaveChildren()

    def num_children(self):
        return self.variant.GetNumChildren() - self.skip_first

    def get_child_at_index(self, index):
        return self.variant.GetChildAtIndex(index + self.skip_first)

    def get_index_of_child(self, name):
        return self.variant.GetIndexOfChildWithName(name) - self.skip_first

    def get_summary(self):
        value_summary = self.variant_name + self.variant_summary

        if self.typename_summary != "":
            return self.typename_summary + "::" + value_summary
        else:
            return value_summary


def get_enum_discriminator_value(union, index):
    obj = union.GetChildAtIndex(index)
    if not obj or obj.GetNumChildren() < 1:
        return None

    discr = obj.GetChildAtIndex(0)
    if not discr or discr.GetName() != "$discr$":
        return None

    return discr.GetValueAsUnsigned()

def enum_summary_provider(valobj, dict):
    return get_synth_summary(GenericEnumSynthProvider, valobj, dict)

def enum_recognizer_function(sbtype, _internal_dict):
    if sbtype.GetNumberOfFields() != 1:
        return False

    if sbtype.GetFieldAtIndex(0).GetName() != "$variants$":
        return False

    name = sbtype.GetName()
    special_cases = ["core::option::Option", "core::result::Result", "alloc::borrow::Cow"]
    for case in special_cases:
        if name.startswith(case):
            return False

    return True


class GenericEnumSynthProvider(EnumSynthProvider):
    def update(self):
        self.summary = ''
        self.variant = self.valobj

        self.valobj.SetPreferSyntheticValue(False)
        union = self.valobj.GetChildAtIndex(0)
        union.SetPreferSyntheticValue(False)

        # at this point we assume this is a rust enum,
        # so if we fail further down the line we report an error
        self.variant_name = '<invalid enum variant>'

        enum_type = self.valobj.GetType()
        if enum_type.IsPointerType():
            enum_name = "&" + \
                unscope_typename(enum_type.GetPointeeType().GetName())
        else:
            enum_name = unscope_typename(enum_type.GetName())
        self.typename_summary = enum_name

        variant_count = union.GetNumChildren()

        discriminator = None
        first_variant_without_discriminator = None

        for i in range(variant_count):
            dc = get_enum_discriminator_value(union, i)
            if dc is None:
                if first_variant_without_discriminator is None:
                    first_variant_without_discriminator = i
                else:
                    return  # multiple variants without discriminator
            else:
                if discriminator is not None:
                    if dc != discriminator:
                        return  # conflicting discriminator values
                else:
                    discriminator = dc

        selected_variant = discriminator

        if first_variant_without_discriminator is not None:
            # probably a pointer based niche
            # all of this is just based on trial and error
            high_bit = 1 << (8 * TARGET_ADDR_SIZE - 1)

            if variant_count == 1:
                selected_variant = 0
            elif discriminator >= high_bit:
                selected_variant = discriminator - high_bit
                if selected_variant >= first_variant_without_discriminator:
                    if selected_variant + 1 < variant_count:
                        selected_variant += 1
            elif discriminator == 0 or discriminator >= variant_count :
                selected_variant = first_variant_without_discriminator

        if selected_variant >= variant_count:
            return

        union.SetPreferSyntheticValue(True)
        variant_outer = union.GetChildAtIndex(selected_variant)

        if variant_outer.GetNumChildren() == 1 and selected_variant == first_variant_without_discriminator:
            variant_outer_subindex = 0
        elif variant_outer.GetNumChildren() != 2:
            return
        else:
            variant_outer_subindex = 1

        variant_outer.SetPreferSyntheticValue(True)
        variant = variant_outer.GetChildAtIndex(variant_outer_subindex)

        # GetTypeName() gives weird results, e.g. `Foo::A:8`. Don't ask me why.
        variant_typename = drop_template_args(unscope_typename(variant.GetType().GetName()))
        self.variant_name = variant_typename

        variant_deref = False

        variant_child_count = variant.GetNumChildren()
        if variant_child_count == 1 and variant.GetChildAtIndex(0).GetName() in ['0', '__0']:
            variant = variant.GetChildAtIndex(0)
            variant_child_count = variant.GetNumChildren()
            variant_deref = True

        if variant_child_count == 0 and variant.GetValue() is None:
            summary = variant.GetSummary()
            if summary is not None:
                self.variant = variant
                self.variant_summary = f"({summary})"
            return

        objname = None
        if variant_deref and variant_child_count != 0:
            objname = variant_typename

        self.variant_summary = obj_summary(
            variant,
            obj_typename=objname,
            parenthesize_single_value=True
        )

        self.variant = variant


class OptionSynthProvider(GenericEnumSynthProvider):
    def update(self):
        super().update()
        self.typename_summary = ""
        # turn `Some<T>(..)` into `Some(..)`
        if self.variant_name.startswith("Some"):
            self.variant_name = "Some"
        elif self.variant_name.startswith("None"):
            self.variant_name = "None"


class ResultSynthProvider(GenericEnumSynthProvider):
    def update(self):
        super().update()
        self.typename_summary = ""
        # turn `Ok<T>(..)` into `Ok(..)`
        if self.variant_name.startswith("Ok"):
            self.variant_name = "Ok"
        elif self.variant_name.startswith("Err"):
            self.variant_name = "Err"


class CowSynthProvider(GenericEnumSynthProvider):
    def update(self):
        super().update()
        self.typename_summary = ""
        # turn `Borrowed<T>(..)` into `Borrowed(..)`
        if self.variant_name.startswith("Borrowed"):
            self.variant_name = "Borrowed"
        elif self.variant_name.startswith("Owned"):
            self.variant_name = "Owned"


class MsvcTupleSynthProvider(RustSynthProvider):
    def update(self):
        tparams = get_template_params(self.valobj.GetTypeName())
        self.type_name = '(' + ', '.join(tparams) + ')'

    def has_children(self):
        return self.valobj.MightHaveChildren()

    def num_children(self):
        return self.valobj.GetNumChildren()

    def get_child_at_index(self, index):
        child = self.valobj.GetChildAtIndex(index)
        return child.CreateChildAtOffset(str(index), 0, child.GetType())

    def get_index_of_child(self, name):
        return str(name)

    def get_summary(self):
        return tuple_summary(self.valobj)

    def get_type_name(self):
        return self.type_name


class MsvcEnumSynthProvider(EnumSynthProvider):
    is_tuple_variant = False

    def update(self):
        tparams = get_template_params(self.valobj.GetTypeName())
        if len(tparams) == 1:  # Regular enum
            discr = gcm(self.valobj, 'discriminant')
            self.variant = gcm(self.valobj, 'variant' +
                               str(discr.GetValueAsUnsigned()))
            variant_name = discr.GetValue()
        else:  # Niche enum
            dataful_min = int(tparams[1])
            dataful_max = int(tparams[2])
            dataful_var = tparams[3]
            discr = gcm(self.valobj, 'discriminant')
            if dataful_min <= discr.GetValueAsUnsigned() <= dataful_max:
                self.variant = gcm(self.valobj, 'dataful_variant')
                variant_name = dataful_var
            else:
                variant_name = discr.GetValue()

        self.type_name = tparams[0]

        if self.variant.IsValid() and self.variant.GetNumChildren() > self.skip_first:
            if self.variant.GetChildAtIndex(self.skip_first).GetName() == '__0':
                self.is_tuple_variant = True
                self.summary = variant_name + \
                    tuple_summary(self.variant, skip_first=self.skip_first)
            else:
                self.summary = variant_name + '{...}'
        else:
            self.summary = variant_name

    def get_child_at_index(self, index):
        child = self.variant.GetChildAtIndex(index + self.skip_first)
        if self.is_tuple_variant:
            return child.CreateChildAtOffset(str(index), 0, child.GetType())
        else:
            return child

    def get_index_of_child(self, name):
        if self.is_tuple_variant:
            return int(name)
        else:
            return self.variant.GetIndexOfChildWithName(name) - self.skip_first

    def get_type_name(self):
        return self.type_name


class MsvcEnum2SynthProvider(EnumSynthProvider):
    is_tuple_variant = False

    def update(self):
        tparams = get_template_params(self.valobj.GetTypeName())

        if len(tparams) == 1:  # Regular enum
            discr = gcm(self.valobj, 'tag')
            self.variant = gcm(self.valobj, 'variant' +
                               str(discr.GetValueAsUnsigned())).GetChildAtIndex(0)
        else:  # Niche enum
            dataful_min = int(tparams[1])
            dataful_max = int(tparams[2])
            discr = gcm(self.valobj, 'tag')
            if dataful_min <= discr.GetValueAsUnsigned() <= dataful_max:
                self.variant = gcm(self.valobj, 'dataful_variant')

        names = re.split("::", self.variant.GetTypeName())
        variant_name = names[-1]
        self.type_name = tparams[0]

        if self.variant.IsValid() and self.variant.GetNumChildren() > self.skip_first:
            if self.variant.GetChildAtIndex(self.skip_first).GetName() == '__0':
                self.is_tuple_variant = True
                self.summary = variant_name + \
                    tuple_summary(self.variant, skip_first=self.skip_first)
            else:
                self.summary = variant_name + " " + obj_summary(self.variant)
        else:
            self.summary = variant_name

    def get_summary(self):
        return self.summary


class StdHashMapSynthProvider(RustSynthProvider):
    def update(self):
        self.initialize_table(gcm(self.valobj, 'base', 'table'))

    def initialize_table(self, table):
        assert table.IsValid()

        if table.type.GetNumberOfTemplateArguments() > 0:
            item_ty = table.type.GetTemplateArgumentType(0)
        else:  # we must be on windows-msvc - try to look up item type by name
            table_ty_name = table.GetType().GetName()  # "hashbrown::raw::RawTable<ITEM_TY>"
            item_ty_name = get_template_params(table_ty_name)[0]
            item_ty = table.GetTarget().FindTypes(item_ty_name).GetTypeAtIndex(0)

        if item_ty.IsTypedefType():
            item_ty = item_ty.GetTypedefedType()

        inner_table = table.GetChildMemberWithName('table')
        if inner_table.IsValid():
            self.initialize_hashbrown_v2(
                inner_table, item_ty)  # 1.52 <= std_version
        else:
            if not table.GetChildMemberWithName('data'):
                self.initialize_hashbrown_v2(
                    table, item_ty)  # ? <= std_version < 1.52
            else:
                self.initialize_hashbrown_v1(
                    table, item_ty)  # 1.36 <= std_version < ?

    def initialize_hashbrown_v2(self, table, item_ty):
        self.num_buckets = gcm(table, 'bucket_mask').GetValueAsUnsigned() + 1
        ctrl_ptr = gcm(table, 'ctrl', 'pointer')
        ctrl = ctrl_ptr.GetPointeeData(0, self.num_buckets)
        # Buckets are located above `ctrl`, in reverse order.
        start_addr = ctrl_ptr.GetValueAsUnsigned() - item_ty.GetByteSize() * \
            self.num_buckets
        buckets_ty = item_ty.GetArrayType(self.num_buckets)
        self.buckets = self.valobj.CreateValueFromAddress(
            'data', start_addr, buckets_ty)
        error = lldb.SBError()
        self.valid_indices = []
        for i in range(self.num_buckets):
            if ctrl.GetUnsignedInt8(error, i) & 0x80 == 0:
                self.valid_indices.append(self.num_buckets - 1 - i)

    def initialize_hashbrown_v1(self, table, item_ty):
        self.num_buckets = gcm(table, 'bucket_mask').GetValueAsUnsigned() + 1
        ctrl_ptr = gcm(table, 'ctrl', 'pointer')
        ctrl = ctrl_ptr.GetPointeeData(0, self.num_buckets)
        buckets_ty = item_ty.GetArrayType(self.num_buckets)
        self.buckets = gcm(
            table, 'data', 'pointer').Dereference().Cast(buckets_ty)
        error = lldb.SBError()
        self.valid_indices = []
        for i in range(self.num_buckets):
            if ctrl.GetUnsignedInt8(error, i) & 0x80 == 0:
                self.valid_indices.append(i)

    def has_children(self):
        return True

    def num_children(self):
        return len(self.valid_indices)

    def get_child_at_index(self, index):
        bucket_idx = self.valid_indices[index]
        item = self.buckets.GetChildAtIndex(bucket_idx)
        item.SetPreferSyntheticValue(True)
        v = item.CreateChildAtOffset('[%d]' % index, 0, item.GetType())
        v.SetPreferSyntheticValue(True)
        return v

    def get_index_of_child(self, name):
        return int(name.lstrip('[').rstrip(']'))

    def get_summary(self):
        return 'size=%d, capacity=%d' % (self.num_children(), self.num_buckets)


class StdHashSetSynthProvider(StdHashMapSynthProvider):
    def update(self):
        table = gcm(self.valobj, 'base', 'map', 'table')  # std_version >= 1.48
        if not table.IsValid():
            table = gcm(self.valobj, 'map', 'base',
                        'table')  # std_version < 1.48
        self.initialize_table(table)

    def get_child_at_index(self, index):
        bucket_idx = self.valid_indices[index]
        item = self.buckets.GetChildAtIndex(bucket_idx).GetChildAtIndex(0)
        return item.CreateChildAtOffset('[%d]' % index, 0, item.GetType())

class CrossbeamAtomicCellSynthProvider(DerefSynthProvider):
    def update(self):
        self.deref = gcm(self.valobj, 'value', 'value', 'value', 'value')
        self.deref.SetPreferSyntheticValue(True)


def __lldb_init_module(debugger_obj, internal_dict):  # pyright: ignore
    initialize_category(debugger_obj, internal_dict)
    print(f"loaded rust-prettifier-for-lldb from {__file__}")
